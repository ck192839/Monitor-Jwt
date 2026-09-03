import http.client, json, random, time, sys, threading

HOST, PORT = "localhost", 8080
REG_TOKEN = sys.argv[1]
N_CLIENTS = int(sys.argv[2]) if len(sys.argv) > 2 else 20
DURATION  = int(sys.argv[3]) if len(sys.argv) > 3 else 30
MODE      = sys.argv[4] if len(sys.argv) > 4 else "burst"

# registered token -> returned by server? we can't read db here; we register by GET /monitor/register
# BUT server only returns success/fail, not the new token. Tokens live in db_client.
import subprocess
MYSQL = r"C:/Program Files/MySQL/MySQL Server 9.5/bin/mysql.exe"
def fetch_tokens():
    out = subprocess.run([MYSQL, "-uroot", "-pgou1", "-N", "-e",
        "select token from monitor.db_client where token <> ''"], capture_output=True, text=True).stdout
    return [t.strip() for t in out.splitlines() if t.strip()]

def register():
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    conn.request("GET", "/monitor/register", headers={"Authorization": REG_TOKEN})
    r = conn.getresponse(); r.read()
    return r.status == 200

def payload():
    return json.dumps({
        "timestamp": int(time.time()*1000),
        "cpuUsage": round(random.uniform(0,100),2),
        "memoryUsage": round(random.uniform(0,100),2),
        "diskUsage": round(random.uniform(0,100),2),
        "networkUpload": random.uniform(0,1e7),
        "networkDownload": random.uniform(0,1e7),
        "diskRead": random.uniform(0,1e7),
        "diskWrite": random.uniform(0,1e7),
    })

def report_loop(token):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    headers = {"Content-Type": "application/json", "Authorization": token}
    ok = fail = 0
    deadline = time.time() + DURATION
    if MODE == "realtime":
        while time.time() < deadline:
            try:
                conn.request("POST", "/monitor/runtime", body=payload(), headers=headers)
                r = conn.getresponse(); r.read()
                if r.status == 200: ok += 1
                else: fail += 1
            except Exception:
                fail += 1
                conn.close(); conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
            time.sleep(10)
    else:
        while time.time() < deadline:
            try:
                conn.request("POST", "/monitor/runtime", body=payload(), headers=headers)
                r = conn.getresponse(); r.read()
                if r.status == 200: ok += 1
                else: fail += 1
            except Exception:
                fail += 1
                conn.close(); conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    return ok, fail

results = []
def runner(i):
    time.sleep(random.uniform(0, 0.5))
    results.append(report_loop(ALL_TOKENS[i]))

if register():
    time.sleep(0.5)
    ALL_TOKENS = fetch_tokens()
    print(f"registered ok, tokens: {len(ALL_TOKENS)}", flush=True)
else:
    print("register failed"); sys.exit(1)

threads = [threading.Thread(target=runner, args=(i,), daemon=True) for i in range(min(N_CLIENTS, len(ALL_TOKENS)))]
for t in threads: t.start()
for t in threads: t.join()
ok = sum(r[0] for r in results); fail = sum(r[1] for r in results)
print(f"done: ok={ok} fail={fail}")

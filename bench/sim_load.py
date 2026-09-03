import http.client, json, random, time, sys, threading, math

HOST, PORT = "127.0.0.1", 8080
DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
N = int(sys.argv[2]) if len(sys.argv) > 2 else 0
TOKENS = [t.strip() for t in open("tokens.txt") if t.strip()]
if N > 0: TOKENS = TOKENS[:N]
PROFILES = json.load(open("profiles.json"))

random.seed(42)
HOSTS = []
for tok in TOKENS:
    p = PROFILES.get(tok) or {"role":"web","mem_total":16,"mem_used":8}
    role = p["role"]
    HOSTS.append({
        "token": tok,
        "mem_total": p["mem_total"],
        "mem_base": p["mem_used"],
        "cpu_base": p.get("cpu_base", 0.35),
        "cpu_wave": p.get("cpu_wave", 0.15),
        "mem_wave": p["mem_total"] * 0.05,           # wave keeps usage under total
        "disk_gb": {"web":120.0,"db":380.0,"cache":60.0,"batch":300.0,"idle":20.0}[role],
        "net_kb":  {"web":12.0,"db":6.0,"cache":40.0,"batch":3.0,"idle":0.2}[role] * 1024,
        "net_wave":{"web":8.0,"db":4.0,"cache":25.0,"batch":2.0,"idle":0.1}[role] * 1024,
        "phase": random.uniform(0, 6.28),
        "period": random.uniform(180, 600),
    })

def payload(h, tnow):
    w = 2*math.pi*((tnow % h["period"]) / h["period"]) + h["phase"]
    cpu = max(0.02, min(0.97, h["cpu_base"] + h["cpu_wave"]*math.sin(w) + random.uniform(-0.04,0.04)))
    headroom = h["mem_total"] - h["mem_base"]
    mem = max(0.3, h["mem_base"] + min(headroom - 0.5, h["mem_wave"]) * (0.5 + 0.5*math.sin(w+0.6)) + random.uniform(-0.1,0.1))
    mem = min(mem, h["mem_total"] * 0.95)
    disk = max(1.0, h["disk_gb"] + random.uniform(-0.4,0.4))
    net_u = max(1.0, h["net_kb"] + h["net_wave"]*math.sin(w+1.2) + random.uniform(-200,200))
    net_d = max(1.0, h["net_kb"]*1.6 + h["net_wave"]*math.sin(w+2.1) + random.uniform(-300,300))
    return json.dumps({
        "timestamp": int(time.time()*1000),
        "cpuUsage": round(cpu, 4),
        "memoryUsage": round(mem, 2),
        "diskUsage": round(disk, 2),
        "networkUpload": round(net_u, 0),
        "networkDownload": round(net_d, 0),
        "diskRead": round(random.uniform(0.3, 25), 2),
        "diskWrite": round(random.uniform(0.2, 18), 2),
    })

def loop(h):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    headers = {"Content-Type": "application/json", "Authorization": h["token"]}
    deadline = time.time() + DURATION
    while time.time() < deadline:
        try:
            conn.request("POST", "/monitor/runtime", body=payload(h, time.time()), headers=headers)
            conn.getresponse().read()
        except Exception:
            conn.close(); conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
        time.sleep(10)

threads = []
for h in HOSTS:
    t = threading.Thread(target=loop, args=(h,), daemon=True)
    time.sleep(random.uniform(0, 0.3))
    t.start(); threads.append(t)
print(f"{len(HOSTS)} clients reporting every 10s for {DURATION}s", flush=True)
for t in threads: t.join()
print("done")

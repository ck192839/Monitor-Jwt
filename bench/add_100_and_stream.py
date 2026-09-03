import http.client
import json
import math
import subprocess
import threading
import time

HOST, PORT = "127.0.0.1", 8080
MYSQL = r"C:/Program Files/MySQL/MySQL Server 9.5/bin/mysql.exe"
ADMIN_JWT = open("jwt.txt", encoding="utf-8").read().strip()
INTERVAL = 10

def request(method, path, body=None, headers=None):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        raw = response.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}
        return response.status, data
    finally:
        conn.close()

def fetch_tokens():
    result = subprocess.run([MYSQL, "-uroot", "-pgou1", "-N", "-e",
                              "select token from monitor.db_client where token <> ''"],
                             capture_output=True, text=True, check=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def register_one():
    status, result = request("GET", "/api/monitor/register",
                             headers={"Authorization": "Bearer " + ADMIN_JWT})
    if status != 200 or result.get("code") != 200:
        raise RuntimeError(f"register token request failed: HTTP {status} {result}")
    status, result = request("GET", "/monitor/register",
                             headers={"Authorization": result.get("data")})
    if status != 200 or result.get("code") != 200:
        raise RuntimeError(f"host registration failed: HTTP {status} {result}")

def detail_payload(index):
    systems = [("x86_64", "Ubuntu", "22.04", "AMD EPYC 7K62"),
               ("x86_64", "Debian", "12", "Intel(R) Xeon(R) Silver 4210"),
               ("x86_64", "CentOS", "7.9", "Intel(R) Xeon(R) Gold 6248R"),
               ("x86_64", "Windows", "11", "AMD Ryzen 9 5950X"),
               ("aarch64", "Ubuntu", "24.04", "ARM Neoverse-N1")]
    arch, os_name, os_version, cpu = systems[index % len(systems)]
    return {"osArch": arch, "osName": os_name, "osVersion": os_version, "osBit": 64,
            "cpuName": cpu, "cpuCore": (index % 6 + 1) * 4,
            "memory": float((index % 4 + 1) * 8),
            "disk": float(120 + (index % 8) * 80),
            "ip": f"10.3.{index // 250}.{index % 250 + 1}"}

def send_detail(token, index):
    body = json.dumps(detail_payload(index), separators=(",", ":"))
    status, result = request("POST", "/monitor/detail", body=body,
                             headers={"Authorization": token, "Content-Type": "application/json"})
    if status != 200 or result.get("code") != 200:
        raise RuntimeError(f"detail upload failed: HTTP {status} {result}")

def runtime_payload(index, now):
    phase = index * 0.37
    cpu = max(0.03, min(0.95, 0.25 + 0.2 * math.sin(now / 120 + phase)))
    total = (index % 4 + 1) * 8.0
    memory = total * (0.35 + 0.12 * math.sin(now / 180 + phase + 1))
    return json.dumps({"timestamp": int(now * 1000), "cpuUsage": round(cpu, 4),
                       "memoryUsage": round(memory, 2),
                       "diskUsage": round(80 + 4 * math.sin(now / 300 + phase), 2),
                       "networkUpload": round(8 * 1024 + 2 * 1024 * math.sin(now / 60 + phase), 0),
                       "networkDownload": round(16 * 1024 + 4 * 1024 * math.sin(now / 75 + phase), 0),
                       "diskRead": round(2 + 3 * abs(math.sin(now / 45 + phase)), 2),
                       "diskWrite": round(1 + 2 * abs(math.sin(now / 55 + phase)), 2)},
                      separators=(",", ":"))

stats = {"ok": 0, "fail": 0}
stats_lock = threading.Lock()

def stream_one(token, index):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    headers = {"Authorization": token, "Content-Type": "application/json"}
    while True:
        try:
            conn.request("POST", "/monitor/runtime",
                         body=runtime_payload(index, time.time()), headers=headers)
            response = conn.getresponse()
            response.read()
            with stats_lock:
                stats["ok" if response.status == 200 else "fail"] += 1
        except Exception:
            with stats_lock:
                stats["fail"] += 1
            conn.close()
            conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
        time.sleep(INTERVAL)

before = set(fetch_tokens())
for i in range(100):
    register_one()
    if (i + 1) % 10 == 0:
        print(f"registered {i + 1}/100", flush=True)

time.sleep(1)
after = fetch_tokens()
new_tokens = [token for token in after if token not in before]
if len(new_tokens) != 100:
    raise RuntimeError(f"expected 100 new tokens, found {len(new_tokens)}")
for index, token in enumerate(new_tokens):
    send_detail(token, index)

print(f"registered 100 hosts; streaming {len(after)} hosts every {INTERVAL}s", flush=True)
for index, token in enumerate(after):
    threading.Thread(target=stream_one, args=(token, index), daemon=True).start()

while True:
    time.sleep(60)
    with stats_lock:
        print(f"stream stats: ok={stats['ok']} fail={stats['fail']}", flush=True)

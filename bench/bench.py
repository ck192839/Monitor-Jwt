import http.client, threading, time, json, statistics, sys

# Load tester. Since the flow limiter is per-IP, all traffic comes from one source,
# so keep total rate under the configured limit (now 10000/10s -> 1000/s safe ceiling).
HOST, PORT = "127.0.0.1", 8080
JWT = open("jwt.txt").read().strip()
CID = open("cid.txt").read().strip()

PATH = sys.argv[1] if len(sys.argv) > 1 else f"/api/monitor/runtime-now?clientId={CID}"
THREADS = int(sys.argv[2]) if len(sys.argv) > 2 else 30
DURATION = int(sys.argv[3]) if len(sys.argv) > 3 else 30
RATE = float(sys.argv[4]) if len(sys.argv) > 4 else 0   # 0 = unlimited
METHOD = "GET"
BODY = None

lat200, lat429, other = [], [], {}
lock = threading.Lock()
deadline = time.time() + DURATION
interval = 1.0 / RATE if RATE > 0 else 0

def worker(tid):
    l200, l429 = [], []
    o = {}
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    headers = {"Authorization": "Bearer " + JWT, "Content-Type": "application/json"}
    seq = tid
    while time.time() < deadline:
        t0 = time.perf_counter()
        try:
            conn.request("GET", PATH, headers=headers)
            r = conn.getresponse(); r.read()
            dt = (time.perf_counter() - t0) * 1000
            if r.status == 200: l200.append(dt)
            elif r.status == 429: l429.append(dt)
            else: o[r.status] = o.get(r.status, 0) + 1
        except Exception as e:
            o[type(e).__name__] = o.get(type(e).__name__, 0) + 1
            conn.close(); conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
        seq += THREADS
        if interval:
            nxt = deadline - (DURATION - seq * interval)
            wait = nxt - time.perf_counter() if False else 0
            time.sleep(interval)  # simple pacing per thread
    with lock:
        lat200.extend(l200); lat429.extend(l429)
        for k, v in o.items(): other[k] = other.get(k, 0) + v

threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
t0 = time.time()
for t in threads: t.start()
for t in threads: t.join()
wall = time.time() - t0
lat200.sort(); lat429.sort()
n, n429 = len(lat200), len(lat429)
print(f"path={PATH} threads={THREADS} duration={DURATION}s rate_cap={RATE or 'none'}")
print(f"HTTP200={n} HTTP429={n429} other={other}")
if n:
    print(f"QPS(200)={n/wall:.0f}  success_rate={n/(n+n429)*100:.2f}%")
    print(f"P50={lat200[int(n*0.5)]:.1f}ms  P95={lat200[int(n*0.95)]:.1f}ms  P99={lat200[int(n*0.99)]:.1f}ms  avg={statistics.mean(lat200):.1f}ms")

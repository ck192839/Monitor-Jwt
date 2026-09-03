import http.client, threading, time, json, statistics, sys, random

HOST, PORT = "127.0.0.1", 8080
TOKENS = [t.strip() for t in open("tokens.txt") if t.strip()]
THREADS = int(sys.argv[1]); DURATION = int(sys.argv[2])

lat200, lat429, other = [], [], {}
lock = threading.Lock()
deadline = time.time() + DURATION

def worker(tid):
    token = TOKENS[tid % len(TOKENS)]
    headers = {"Authorization": token, "Content-Type": "application/json"}
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    l200, l429, o = [], [], {}
    while time.time() < deadline:
        payload = json.dumps({
            "timestamp": int(time.time()*1000),
            "cpuUsage": round(random.uniform(0,100),2),
            "memoryUsage": round(random.uniform(0,100),2),
            "diskUsage": round(random.uniform(0,100),2),
            "networkUpload": random.uniform(0,1e7),
            "networkDownload": random.uniform(0,1e7),
            "diskRead": random.uniform(0,1e7),
            "diskWrite": random.uniform(0,1e7),
        })
        t0 = time.perf_counter()
        try:
            conn.request("POST", "/monitor/runtime", body=payload, headers=headers)
            r = conn.getresponse(); r.read()
            dt = (time.perf_counter()-t0)*1000
            if r.status == 200: l200.append(dt)
            elif r.status == 429: l429.append(dt)
            else: o[r.status] = o.get(r.status,0)+1
        except Exception as e:
            o[type(e).__name__] = o.get(type(e).__name__,0)+1
            conn.close(); conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    with lock:
        lat200.extend(l200); lat429.extend(l429)
        for k,v in o.items(): other[k] = other.get(k,0)+v

threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
t0=time.time()
for t in threads: t.start()
for t in threads: t.join()
wall=time.time()-t0
lat200.sort(); lat429.sort()
n=len(lat200)
print(f"POST /monitor/runtime threads={THREADS} duration={DURATION}s")
print(f"HTTP200={n} HTTP429={len(lat429)} other={other}")
if n:
    print(f"QPS={n/wall:.0f}")
    print(f"P50={lat200[int(n*0.5)]:.1f}ms P95={lat200[int(n*0.95)]:.1f}ms P99={lat200[int(n*0.99)]:.1f}ms avg={statistics.mean(lat200):.1f}ms")

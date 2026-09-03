import http.client, time, urllib.parse
for i in range(3):
    conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=15)
    q = urllib.parse.urlencode({"email": "1946695793@qq.com", "type": "reset"})
    t0 = time.perf_counter()
    conn.request("GET", f"/api/auth/ask-code?{q}")
    r = conn.getresponse(); body = r.read()
    print(f"ask-code#{i+1}: {r.status} {(time.perf_counter()-t0)*1000:.0f}ms", flush=True)
    if i < 2: time.sleep(61)

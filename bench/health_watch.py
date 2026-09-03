import http.client, json, time
JWT = open("jwt.txt").read().strip()
ok = bad = 0
start = time.time()
while True:
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=5)
        conn.request("GET", "/api/monitor/list", headers={"Authorization": "Bearer "+JWT})
        r = conn.getresponse(); d = json.loads(r.read())
        data = d.get("data") or []
        unsafe = sum(1 for c in data if c["cpuUsage"]*100 > 100 or c["memoryUsage"]/c["memory"]*100 > 100)
        if r.status == 200 and d["code"] == 200 and len(data) >= 12 and unsafe == 0:
            ok += 1; state = "ok"
        else:
            bad += 1; state = f"BAD http={r.status} hosts={len(data)} unsafe_cards={unsafe}"
    except Exception as e:
        bad += 1; state = f"EXC {type(e).__name__}"
    print(f"[{time.strftime('%H:%M:%S')}] {state} ok={ok} bad={bad} elapsed={int(time.time()-start)}s", flush=True)
    time.sleep(5)

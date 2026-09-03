import http.client, json, subprocess

MYSQL = r"C:/Program Files/MySQL/MySQL Server 9.5/bin/mysql.exe"
rows = subprocess.run([MYSQL, "-uroot", "-pgou1", "-N", "-e",
    "select id, token from monitor.db_client"], capture_output=True, text=True).stdout.splitlines()
for i, line in enumerate(rows):
    cid, tok = line.split("\t")
    detail = {
        "osArch": "amd64", "osName": "Windows", "osVersion": "10", "osBit": 64,
        "cpuName": "Virtual CPU", "cpuCore": 8, "memory": 16.0,
        "disk": 512.0, "ip": f"192.168.56.{15+i}",
    }
    conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=10)
    conn.request("POST", "/monitor/detail", body=json.dumps(detail),
                 headers={"Authorization": tok, "Content-Type": "application/json"})
    r = conn.getresponse()
    print(cid, r.status, r.read()[:60])
    conn.close()

import subprocess, http.client, json, random
MYSQL = r"C:/Program Files/MySQL/MySQL Server 9.5/bin/mysql.exe"
out = subprocess.run([MYSQL, "-uroot", "-pgou1", "-N", "-e",
    "select id, token from monitor.db_client"], capture_output=True, text=True).stdout
rows = [l.split("\t") for l in out.splitlines() if l.strip()]
random.seed(7)
LOC = ["cn","hk","jp","us","sg","kr","de"]
OS = [("Windows","11"),("Windows","10"),("Ubuntu","22.04"),("Ubuntu","20.04"),("CentOS","7.9"),("Debian","12")]
CPU = ["Intel(R) Xeon(R) Silver 4210","AMD EPYC 7K62","Intel(R) Core(TM) i9-13900K","AMD Ryzen 9 5950X","Intel(R) Xeon(R) Gold 6248R"]
profiles = {}
for i,(cid, tok) in enumerate(rows):
    role = ["web","db","cache","batch","idle"][i%5]
    mem_total = {"web":16,"db":64,"cache":32,"batch":64,"idle":8}[role]
    mem_used = round(mem_total*random.uniform(0.25,0.75),1)
    profiles[cid] = {"role":role, "mem_total":mem_total, "mem_used":mem_used}
    detail = {
        "osArch":"amd64","osName":OS[i%len(OS)][0],"osVersion":OS[i%len(OS)][1],"osBit":64,
        "cpuName":CPU[i%len(CPU)],"cpuCore":[4,8,16,24][i%4],"memory":float(mem_total),
        "disk":512.0,"ip":f"10.{(i//250)%250+2}.{i%250}.{(i*7)%250}",
    }
    conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=10)
    conn.request("POST", "/monitor/detail", body=json.dumps(detail),
                 headers={"Authorization": tok, "Content-Type": "application/json"})
    conn.getresponse().read(); conn.close()
json.dump(profiles, open("profiles.json","w"))
print("reprofiled", len(rows), "hosts")

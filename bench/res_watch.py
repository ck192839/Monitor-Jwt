import subprocess, time, re

def sample():
    out = subprocess.run([
        "powershell","-Command",
        "$t0=(Get-Process -Id (Get-NetTCPConnection -LocalPort 8080 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess));"
        "$c0=$t0.TotalProcessorTime.TotalSeconds; Start-Sleep -m 500;"
        "$t1=Get-Process -Id $t0.Id; $c1=$t1.TotalProcessorTime.TotalSeconds;"
        "$cpu=Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average;"
        "$os=Get-CimInstance Win32_OperatingSystem;"
        "$javaPct=[math]::Round((($c1-$c0)/0.5)*100/16,1);"
        "$javaMem=[int]($t1.WorkingSet64/1MB);"
        "Write-Output \"$javaPct $javaMem $([int]$cpu) $([int](($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/1KB))\""
    ], capture_output=True, text=True).stdout.strip()
    return out

samples = []
for i in range(3):
    s = sample()
    if s: samples.append(s.split())
    time.sleep(4)
# avg
try:
    jp = sum(float(s[0]) for s in samples)/len(samples)
    jm = sum(float(s[1]) for s in samples)/len(samples)
    sc = sum(float(s[2]) for s in samples)/len(samples)
    sm = sum(float(s[3]) for s in samples)/len(samples)
    print(f"SERVER_JAVA_CPU%={jp:.0f} SERVER_JAVA_MEM_MB={jm:.0f} SYS_CPU%={sc:.0f} SYS_MEM_USED_MB={sm:.0f}")
except Exception as e:
    print("parse fail:", samples)

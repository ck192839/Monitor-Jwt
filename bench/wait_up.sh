#!/bin/bash
for i in $(seq 1 600); do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "http://localhost:8080/api/monitor/list" -H "Authorization: Bearer $(cat jwt.txt)" 2>/dev/null)
  if [ "$code" = "200" ] || [ "$code" = "401" ]; then echo "UP http=$code at $(date +%H:%M:%S)"; exit 0; fi
  sleep 5
done
echo "still down after 50min"

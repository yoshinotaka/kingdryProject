#!/bin/bash

LOG_DIR="/var/www/html/kingProject/resource_monitor/logs/"
mkdir -p "$LOG_DIR"

DATE=$(date '+%Y%m%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

DOCKER_LOG_FILE="$LOG_DIR/docker_stats_$DATE.log"
HOSTMEM_LOG_FILE="$LOG_DIR/host_mem_$DATE.log"
PS_LOG_FILE="$LOG_DIR/ps_top_mem_$DATE.log"

# docker statsヘッダー追加（ファイルが存在しないときのみ）
if [ ! -f "$DOCKER_LOG_FILE" ]; then
    echo -e "Timestamp            ContainerID        ContainerName              CPU%     MemUsage                Mem%    NetIO                BlockIO              PIDs" >> "$DOCKER_LOG_FILE"
fi

# host memヘッダー
if [ ! -f "$HOSTMEM_LOG_FILE" ]; then
    echo -e "Timestamp            total     used     free    shared  buff/cache  available  swap_total swap_used swap_free" >> "$HOSTMEM_LOG_FILE"
fi

# ps auxヘッダー
if [ ! -f "$PS_LOG_FILE" ]; then
    echo -e "Timestamp            USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND" >> "$PS_LOG_FILE"
fi

# docker stats
docker stats --no-stream --format "{{.Container}},{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" \
| while IFS=, read -r container_id container_name cpu mem_usage mem_perc net_io block_io pids; do
    printf "%-20s %-18s %-26s %-8s %-22s %-8s %-20s %-20s %-5s\n" \
      "$TIMESTAMP" "$container_id" "$container_name" "$cpu" "$mem_usage" "$mem_perc" "$net_io" "$block_io" "$pids" >> "$DOCKER_LOG_FILE"
done

# free -m によるメモリ出力
MEM_LINE=$(free -m | awk '/Mem:/ {print $2, $3, $4, $5, $6, $7}')
SWAP_LINE=$(free -m | awk '/Swap:/ {print $2, $3, $4}')
printf "%-20s %s %s\n" "$TIMESTAMP" "$MEM_LINE" "$SWAP_LINE" >> "$HOSTMEM_LOG_FILE"

# ps aux 出力（上位20プロセス）
printf "%-20s\n" "$TIMESTAMP" >> "$PS_LOG_FILE"
ps aux --sort=-%mem | head -21 | tail -20 >> "$PS_LOG_FILE"
echo "" >> "$PS_LOG_FILE"

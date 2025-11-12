# -*- coding: utf-8 -*-
"""
Problem Statement 2: System Health Monitoring Script
---------------------------------------------------
This script monitors the system’s CPU, memory, disk usage, and running processes.
It prints real-time system health metrics and warns when thresholds are exceeded.
"""


import psutil
import platform
import time
import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------

THRESHOLDS = {
    "cpu": 80,       # Warn if CPU usage exceeds 80%
    "memory": 80,    # Warn if memory usage exceeds 80%
    "disk": 85       # Warn if disk usage exceeds 85%
}

MONITOR_INTERVAL = 5  # seconds between checks
LOG_FILE = "system_health_log.txt"


# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------

def log_message(message):
    """Logs message to console and file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def get_system_info():
    """Returns basic system information."""
    uname = platform.uname()
    return {
        "System": uname.system,
        "Node Name": uname.node,
        "Release": uname.release,
        "Version": uname.version,
        "Machine": uname.machine,
        "Processor": uname.processor
    }


def check_cpu_usage():
    """Checks CPU usage and warns if it exceeds threshold."""
    cpu_percent = psutil.cpu_percent(interval=1)
    status = "⚠️ High CPU Usage" if cpu_percent > THRESHOLDS["cpu"] else "✅ Normal"
    log_message(f"CPU Usage: {cpu_percent}% — {status}")
    return cpu_percent


def check_memory_usage():
    """Checks memory usage and warns if it exceeds threshold."""
    memory = psutil.virtual_memory()
    percent = memory.percent
    status = "⚠️ High Memory Usage" if percent > THRESHOLDS["memory"] else "✅ Normal"
    log_message(f"Memory Usage: {percent}% ({round(memory.used / (1024**3), 2)} GB used) — {status}")
    return percent


def check_disk_usage():
    """Checks disk usage and warns if it exceeds threshold."""
    disk = psutil.disk_usage("/")
    percent = disk.percent
    status = "⚠️ Disk Space Low" if percent > THRESHOLDS["disk"] else "✅ Normal"
    log_message(f"Disk Usage: {percent}% ({round(disk.used / (1024**3), 2)} GB used) — {status}")
    return percent


def list_top_processes(limit=5):
    """Lists top processes by CPU usage."""
    log_message(f"Top {limit} Processes by CPU Usage:")
    processes = [(p.info["pid"], p.info["name"], p.info["cpu_percent"])
                 for p in psutil.process_iter(["pid", "name", "cpu_percent"])]
    sorted_procs = sorted(processes, key=lambda x: x[2], reverse=True)[:limit]
    for pid, name, cpu in sorted_procs:
        log_message(f"   PID={pid} | {name} | CPU={cpu}%")
    log_message("-" * 50)


# ----------------------------
# MAIN MONITORING LOOP
# ----------------------------

def monitor_system():
    """Main loop to monitor system health."""
    system_info = get_system_info()
    log_message("========== SYSTEM HEALTH MONITOR ==========")
    for key, value in system_info.items():
        log_message(f"{key}: {value}")
    log_message("==========================================")

    try:
        while True:
            log_message("\n📊 Checking system health...")
            cpu = check_cpu_usage()
            mem = check_memory_usage()
            disk = check_disk_usage()
            list_top_processes(limit=5)

            if cpu > THRESHOLDS["cpu"] or mem > THRESHOLDS["memory"] or disk > THRESHOLDS["disk"]:
                log_message("🚨 ALERT: One or more thresholds exceeded! Please investigate.\n")

            time.sleep(MONITOR_INTERVAL)
    except KeyboardInterrupt:
        log_message("\n🛑 Monitoring stopped by user.")
        log_message("==========================================\n")


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    monitor_system()

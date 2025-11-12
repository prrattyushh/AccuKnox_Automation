# -*- coding: utf-8 -*-
"""
Problem Statement 2: Automated Backup Solution
----------------------------------------------
This script automates backup creation for a specified directory.
It compresses the directory, uploads it to a remote server (via SCP),
and generates a report on success or failure.
"""

import os
import tarfile
import time
import datetime
import paramiko
from pathlib import Path

# ----------------------------
# CONFIGURATION
# ----------------------------

# Directory to back up (change this to your local folder)
SOURCE_DIR = r"C:\Users\Pratyush\Documents\ImportantData"

# Where to store the backup locally before upload
BACKUP_DIR = r"C:\Users\Pratyush\Backups"

# Remote server (if not using remote backup, leave REMOTE_ENABLED = False)
REMOTE_ENABLED = False
REMOTE_CONFIG = {
    "hostname": "your.remote.server.com",
    "port": 22,
    "username": "your_username",
    "password": "your_password",
    "remote_path": "/home/your_username/backups/"
}

# Backup metadata
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_NAME = f"backup_{TIMESTAMP}.tar.gz"
LOCAL_BACKUP_PATH = os.path.join(BACKUP_DIR, BACKUP_NAME)

# Report file
REPORT_FILE = "backup_report.txt"


# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------

def log_message(message):
    """Logs message to console and report file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def create_backup(source_dir, destination_path):
    """Create a tar.gz backup of the specified directory."""
    log_message(f"📦 Starting backup of '{source_dir}'...")
    start_time = time.time()
    try:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with tarfile.open(destination_path, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        elapsed = time.time() - start_time
        size = os.path.getsize(destination_path) / (1024 * 1024)
        log_message(f"✅ Backup created successfully: {destination_path}")
        log_message(f"   Size: {size:.2f} MB | Time taken: {elapsed:.2f} sec")
        return True
    except Exception as e:
        log_message(f"❌ Failed to create backup: {e}")
        return False


def upload_backup_scp(local_path, remote_config):
    """Upload backup to remote server using SCP (via paramiko)."""
    try:
        log_message(f"🌐 Connecting to remote server {remote_config['hostname']}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            remote_config["hostname"],
            port=remote_config["port"],
            username=remote_config["username"],
            password=remote_config["password"]
        )
        sftp = ssh.open_sftp()
        remote_path = os.path.join(remote_config["remote_path"], os.path.basename(local_path))
        log_message(f"⬆️ Uploading backup to remote path: {remote_path}")
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()
        log_message("✅ Backup uploaded successfully to remote server.")
        return True
    except Exception as e:
        log_message(f"❌ Remote upload failed: {e}")
        return False


def generate_summary(success_local, success_remote):
    """Generate summary of the backup operation."""
    log_message("\n================ BACKUP SUMMARY ================")
    log_message(f"Source Directory: {SOURCE_DIR}")
    log_message(f"Backup File: {LOCAL_BACKUP_PATH}")
    log_message(f"Remote Upload: {'Enabled' if REMOTE_ENABLED else 'Disabled'}")
    log_message(f"Local Backup Status: {'✅ Success' if success_local else '❌ Failed'}")
    if REMOTE_ENABLED:
        log_message(f"Remote Upload Status: {'✅ Success' if success_remote else '❌ Failed'}")
    log_message("===============================================\n")


# ----------------------------
# MAIN EXECUTION
# ----------------------------

def main():
    log_message("🚀 Automated Backup Process Initiated")
    log_message(f"Timestamp: {TIMESTAMP}")
    
    # Step 1: Create backup
    success_local = create_backup(SOURCE_DIR, LOCAL_BACKUP_PATH)
    
    # Step 2: Upload to remote if enabled
    success_remote = False
    if REMOTE_ENABLED and success_local:
        success_remote = upload_backup_scp(LOCAL_BACKUP_PATH, REMOTE_CONFIG)
    
    # Step 3: Generate summary
    generate_summary(success_local, success_remote)
    
    if success_local and (success_remote or not REMOTE_ENABLED):
        log_message("🎉 Backup process completed successfully.")
    else:
        log_message("⚠️ Backup process encountered issues.")
    
    log_message("📁 Detailed report saved to 'backup_report.txt'")


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()

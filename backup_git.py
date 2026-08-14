#!/usr/bin/env python3

#chmod +x /mnt/UDISK/printer_data/config/backup_git.py

import os
import json
import base64
import urllib.request
from urllib.error import HTTPError
import glob

# Configuration variables
TOKEN = "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"
REPO = "Barconero/My-K2-Pro-config"
DIR = "/mnt/UDISK/printer_data/config"

os.chdir(DIR)

# Find all configuration files
files = glob.glob("*.cfg") + glob.glob("*.conf")

for file_name in files:
    print(f"Processing {file_name}...")
    
    # 1. Read and encode the file content in Base64
    try:
        with open(file_name, "rb") as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        continue

    url = f"https://api.github.com/repos/{REPO}/contents/{file_name}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 2. Check if the file already exists on GitHub to retrieve its SHA
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            sha = res_data.get("sha")
    except HTTPError as e:
        if e.code == 404:
            pass # File does not exist yet, proceed with creation
        else:
            print(f"API error while checking {file_name}: {e.code}")
            continue
    except Exception as e:
        print(f"Network error: {e}")
        continue
        
    # 3. Prepare the JSON payload
    payload = {
        "message": f"auto-update {file_name}",
        "content": encoded_content
    }
    
    if sha:
        payload["sha"] = sha # Required by GitHub API when updating existing files
        
    data = json.dumps(payload).encode('utf-8')
    
    # 4. Send the PUT request to upload the file
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as response:
            print(f"Success: {file_name} uploaded.")
    except HTTPError as e:
        print(f"Upload error for {file_name}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Unknown error: {e}")

print("Backup successfully completed!")


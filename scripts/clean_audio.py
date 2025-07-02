import os
import time
import requests
import argparse

API_KEY = os.environ.get('AUPHONIC_API_KEY')
BASE_URL = "https://auphonic.com/api"

def exit_with_error(msg, response=None):
    print(f"ERROR: {msg}")
    if response is not None:
        print("Full response content:")
        try:
            print(response.status_code, response.text)
        except Exception as e:
            print("Could not print response:", e)
    exit(1)

def check_file_exists(path):
    if not os.path.isfile(path):
        exit_with_error(f"Audio file does not exist: {path}")
    if not os.access(path, os.R_OK):
        exit_with_error(f"Audio file is not readable: {path}")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Upload audio file to Auphonic for processing')
parser.add_argument('file_path', help='Path to the audio file to process')
parser.add_argument('--preset', '-p', default='Usual-2', help='Preset name to use (default: Usual-2)')
parser.add_argument('--output-dir', '-o', default='~/Downloads/auphonic_results', help='Output directory for processed files')

args = parser.parse_args()

AUDIO_FILE = os.path.expanduser(args.file_path)
PRESET_NAME = args.preset
OUTPUT_DIR = os.path.expanduser(args.output_dir)

os.makedirs(OUTPUT_DIR, exist_ok=True)

check_file_exists(AUDIO_FILE)

headers = {"Authorization": f"Bearer {API_KEY}"}

# 1. Find preset UUID by name
print("Looking up preset:", PRESET_NAME)
presets_resp = requests.get(f"{BASE_URL}/presets.json?minimal_data=1", headers=headers)
if presets_resp.status_code != 200:
    exit_with_error("Failed to fetch presets.", presets_resp)
presets = presets_resp.json()
preset_uuid = None
for preset in presets.get("data", []):
    if preset.get("preset_name") == PRESET_NAME:
        preset_uuid = preset.get("uuid")
        break
if not preset_uuid:
    print("Preset not found. Available presets:")
    for preset in presets.get("data", []):
        print("-", preset.get("preset_name"))
    exit(1)

# 2. Upload file and create production
print(f"Uploading file: {AUDIO_FILE}")
try:
    with open(AUDIO_FILE, "rb") as f:
        files = {"input_file": f}
        data = {
            "title": f"Processed {os.path.basename(AUDIO_FILE)}"
        }
        # Only add preset if it's not None
        if preset_uuid:
            data["preset"] = preset_uuid
            print(f"Using preset UUID: {preset_uuid}")
        # Create production without auto-starting
        resp = requests.post(f"{BASE_URL}/simple/productions.json", headers=headers, data=data, files=files)
except Exception as exc:
    exit_with_error(f"Could not open or upload file: {exc}")
if resp.status_code != 200:
    exit_with_error("File upload and production creation failed.", resp)
prod = resp.json()
production_uuid = prod.get("data", {}).get("uuid")
if not production_uuid:
    exit_with_error("Failed to get a valid production_uuid after upload.", resp)

print("Production created:", production_uuid)
print("Monitor at: https://auphonic.com/engine/status/" + production_uuid)

# Now start the production with a small delay to ensure it's ready
time.sleep(2)
print("Starting production...")
start_resp = requests.post(f"{BASE_URL}/production/{production_uuid}/start.json", headers=headers)
if start_resp.status_code != 200:
    print(f"Start response status: {start_resp.status_code}")
    print(f"Start response: {start_resp.text}")
    # Check if it's already started or queued
    current_status_resp = requests.get(f"{BASE_URL}/production/{production_uuid}/status.json", headers=headers)
    if current_status_resp.status_code == 200:
        current_status = current_status_resp.json().get("data", {}).get("status")
        if current_status in [1, 2, 3]:  # Waiting, Processing, or Done
            print("Production appears to be already started or completed")
        else:
            exit_with_error("Failed to start production.", start_resp)
    else:
        exit_with_error("Failed to start production.", start_resp)
else:
    print("Production started successfully")

# 3. Wait for processing to complete
max_wait_time = 300  # 5 minutes maximum
start_time = time.time()

# Give the production a moment to start processing
time.sleep(5)

while True:
    status_resp = requests.get(f"{BASE_URL}/production/{production_uuid}/status.json", headers=headers).json()
    if status_resp is None:
        exit_with_error("Failed to get status response (None).")
    status = status_resp.get("data", {}).get("status")
    status_str = status_resp.get("data", {}).get("status_string")
    print(f"Status: {status_str} (code: {status})")
    
    if status == 3:
        print("Processing complete!")
        break
    
    # Status 4 is "Audio Processing" - still in progress, not a failure
    if status in [1, 2, 4]:  # Waiting, Processing, Audio Processing
        # Continue waiting
        pass
    elif status == 5:  # This would be an actual error status
        print("Processing failed! Getting detailed error information...")
        details_resp = requests.get(f"{BASE_URL}/production/{production_uuid}.json", headers=headers)
        if details_resp.status_code != 200:
            exit_with_error("Failed to fetch production details after processing failure", details_resp)
        print("Full production details below for debugging:")
        print(details_resp.text)
        try:
            details = details_resp.json()
            data = details.get("data", {})
            print(f"Error Summary: {data.get('error_summary', 'No summary available')}")
            print(f"Error Message: {data.get('error_message', 'No detailed message available')}")
            print(f"Warning Message: {data.get('warning_message', 'No warnings')}")
        except Exception as e:
            print(f"Could not parse details JSON: {e}")
        exit(1)
    else:
        print(f"Unknown status code: {status}. Continuing to wait...")
    
    # Check for timeout
    if time.time() - start_time > max_wait_time:
        print(f"Processing timed out after {max_wait_time} seconds")
        print("You can check the status manually at: https://auphonic.com/engine/status/" + production_uuid)
        exit(1)
    
    time.sleep(15)  # Wait longer between checks

# 4. Download result files
details_resp = requests.get(f"{BASE_URL}/production/{production_uuid}.json", headers=headers)
if details_resp.status_code != 200:
    exit_with_error("Failed to fetch output files for completed production.", details_resp)
details = details_resp.json()
for f in details.get("data", {}).get("output_files", []):
    url = f.get("download_url")
    filename = f.get("filename")
    if url and filename:
        print("Downloading:", filename)
        r = requests.get(url, headers=headers, allow_redirects=True)
        if r.status_code != 200:
            exit_with_error(f"Download of {filename} failed.", r)
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "wb") as out:
            out.write(r.content)
        print("Saved to:", out_path)

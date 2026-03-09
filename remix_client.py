import argparse
import base64
import json
import os
import requests
import time

# To use this script, Marcel needs to set his RunPod Endpoint ID and API Key
# Either export them as environment variables, or hardcode them here (not recommended for sharing)
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY", "YOUR_API_KEY_HERE")
RUNPOD_ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID", "YOUR_ENDPOINT_ID_HERE")

def separate_audio(input_file, output_dir):
    """
    Sends the local audio file to the RunPod API, waits for processing,
    and decodes the Base64 responses back into .wav files.
    """
    if not os.path.exists(input_file):
        print(f"Error: Could not find file {input_file}")
        return

    print(f"Loading {input_file}...")
    with open(input_file, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Construct the API request payload
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {
            "audio_base64": audio_base64
        }
    }

    print("Uploading to RunPod Cloud (this may take a minute based on your internet speed)...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Failed to submit job. Status code: {response.status_code}")
        print(response.text)
        return

    job_id = response.json().get("id")
    print(f"Job successfully started! Job ID: {job_id}")

    # Wait for the job to complete
    status_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"
    print("Processing audio with Demucs in the cloud...", end="")
    
    while True:
        status_response = requests.get(status_url, headers=headers)
        if status_response.status_code != 200:
            print("\nError fetching status.")
            return
            
        status_data = status_response.json()
        status = status_data.get("status")
        
        if status == "COMPLETED":
            print("\nDone!")
            break
        elif status == "FAILED":
            print("\nJob failed on RunPod.")
            print(status_data)
            return
        
        print(".", end="", flush=True)
        time.sleep(3) # Check status every 3 seconds

    # Extract the base64 files from the output and write them to disk
    output = status_data.get("output", {})
    if output.get("status") == "success":
        os.makedirs(output_dir, exist_ok=True)
        stems_base64 = output.get("stems_base64", {})
        
        for stem_name, encoded_audio in stems_base64.items():
            file_path = os.path.join(output_dir, f"{stem_name}.wav")
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(encoded_audio))
            print(f"Saved: {file_path}")
            
        print(f"\nSuccessfully downloaded all stems to {output_dir}")
    else:
        print("\nAPI returned an error:")
        print(output.get("error", "Unknown error"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunPod Serverless Client for Demucs Stem Separation")
    parser.add_argument("input_file", help="Path to your local audio file (.wav or .mp3)")
    parser.add_argument("--output_dir", "-o", default="./output_stems", help="Directory to save the separated stems")
    
    args = parser.parse_args()
    separate_audio(args.input_file, args.output_dir)

import runpod
import base64
import tempfile
import subprocess
import os
import requests
import uuid

def process_audio(job):
    """
    RunPod Serverless Handler for Demucs.
    Expects JSON input:
    {
        "input": {
            "audio_url": "https://url-to-audio.com/file.wav"  <-- Optional: Download from URL
            OR
            "audio_base64": "base64_encoded_string..."      <-- Optional: Direct upload
        }
    }
    """
    job_input = job.get("input", {})
    audio_url = job_input.get("audio_url")
    audio_base64 = job_input.get("audio_base64")

    if not audio_url and not audio_base64:
        return {"error": "Must provide either 'audio_url' or 'audio_base64' in input."}

    # Create a temporary workspace for this job
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input_audio.wav")
        output_dir = os.path.join(temp_dir, "demucs_output")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Acquire the Audio
        try:
            if audio_base64:
                print("Decoding base64 audio...")
                with open(input_path, "wb") as f:
                    f.write(base64.b64decode(audio_base64))
            elif audio_url:
                print(f"Downloading audio from {audio_url}...")
                response = requests.get(audio_url)
                response.raise_for_status()
                with open(input_path, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            return {"error": f"Failed to acquire audio: {str(e)}"}

        # 2. Run Demucs
        print("Running Demucs stem separation...")
        try:
            # -n htdemucs is the default model. We output to our temp directory.
            command = [
                "demucs",
                "-n", "htdemucs",
                "--out", output_dir,
                input_path
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Demucs finished successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Demucs Error: {e.stderr}")
            return {"error": f"Demucs processing failed: {e.stderr}"}

        # Demucs places files in output_dir / htdemucs / input_audio / [bass|drums|other|vocals].wav
        model_out_dir = os.path.join(output_dir, "htdemucs", "input_audio")
        
        if not os.path.exists(model_out_dir):
            return {"error": "Demucs output directory not found."}

        # 3. Read Stems and encode to Base64 to return to client
        results = {}
        stems = ["bass.wav", "drums.wav", "other.wav", "vocals.wav"]
        
        for stem in stems:
            stem_path = os.path.join(model_out_dir, stem)
            if os.path.exists(stem_path):
                with open(stem_path, "rb") as f:
                    encoded_stem = base64.b64encode(f.read()).decode("utf-8")
                    stem_name = stem.replace('.wav', '')
                    results[stem_name] = encoded_stem
            else:
                return {"error": f"Expected stem {stem} was not generated."}

        print("Job complete, returning stems.")
        return {
            "status": "success",
            "message": "Stem separation complete",
            "stems_base64": results
        }

# Start the Serverless Worker
runpod.serverless.start({"handler": process_audio})

# How to Deploy and Use the Serverless API

We have built 4 files inside the `runpod_serverless` folder. Here is how to deploy it on RunPod, and how Marcel will use it on his Mac.

---

## 1. Deploying the API (What you need to do on RunPod)

Since we want to avoid slow local internet speeds, you will build the Docker image directly inside Marcel's RunPod account.

1. Rent a cheap GPU Pod on RunPod (e.g., RTX 3090) or a CPU pod if you prefer.
2. Open Jupyter Lab.
3. Upload the `Dockerfile`, `requirements.txt`, and `runpod_worker.py` files to the `/workspace` folder.
4. Open the pod terminal and run this command to build the image and push it to a free Docker Hub account:

```bash
# Log in to Docker Hub (create a free account if you don't have one)
docker login

# Build the custom API image
docker build -t YOUR_DOCKER_USERNAME/marcel_remix_api:v1 .

# Push it to the cloud
docker push YOUR_DOCKER_USERNAME/marcel_remix_api:v1
```

5. Go to the **RunPod Dashboard -> Serverless -> Endpoints -> New Endpoint**.
   - **Image URI:** `YOUR_DOCKER_USERNAME/marcel_remix_api:v1`
   - **GPU Type:** RTX 3090 (or similar)
6. Once deployed, get the **Endpoint ID** and the **RunPod API Key** from the dashboard.

---

## 2. Running on Marcel's Mac (What Marcel will do)

Once the API is live, Marcel never needs to touch RunPod or Docker again. 

1. On his Mac, put the `remix_client.py` file in a folder.
2. He needs to set his RunPod credentials in his terminal (or you can edit the Python script to hardcode them):
```bash
export RUNPOD_API_KEY="his_api_key_here"
export RUNPOD_ENDPOINT_ID="his_endpoint_id_here"
```
3. He installs `requests` if he doesn't have it:
```bash
pip install requests
```
4. He runs the tool on any local audio file!
```bash
python remix_client.py ./my_cool_song.mp3 -o ./my_stems
```

The script will automatically upload the song to the API, wait for the AI to process it, and instantly download the separated `bass.wav`, `drums.wav`, `vocals.wav`, and `other.wav` directly to his local folder!

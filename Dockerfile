# Base image: Official RunPod PyTorch with CUDA 11.8
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg is essential for audio manipulation)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    pkg-config \
    build-essential \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Demucs model so it doesn't download on every API request
RUN python -c "import torch; from demucs.pretrained import get_model; get_model('htdemucs')"

# Copy the serverless worker code
COPY runpod_worker.py .

# CMD specifies the default command to run when the container starts.
CMD ["python", "-u", "runpod_worker.py"]

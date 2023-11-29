# Use the official CUDA 11.8 base image
FROM europe-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-12.py310:latest

WORKDIR /

LABEL com.nvidia.volumes.needed=nvidia_driver

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


# Set the entrypoint command
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
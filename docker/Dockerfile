# Use the official CUDA 11.8 base image
FROM nvidia/cuda:11.8.0-base-ubuntu22.04
RUN apt-get update -y \
    && apt-get install -y python3-pip
# Set environment variables for configuration

# Install vllm
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RUN --mount=type=cache,target=/root/.cache/pip \
   pip install https://github.com/vllm-project/vllm/releases/download/v0.2.1/vllm-0.2.1-cp310-cp310-manylinux1_x86_64.whl
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install xformers==0.0.22

# Set the entrypoint command
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
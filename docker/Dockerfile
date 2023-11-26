FROM nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu20.04 AS dev

ENV VLLM_VERSION=1.0.0
ENV CUDA_VERSION=12.0
 
# Set default values for environment variables
ENV VLLM_HOME=/opt/vllm
ENV CUDA_HOME=/usr/local/cuda

RUN apt-get update -y \
    && apt-get install -y python3-pip

WORKDIR $VLLM_HOME
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
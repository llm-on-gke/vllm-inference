FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime AS dev

ENV VLLM_VERSION=1.0.0
ENV CUDA_VERSION=12.0.0
 
# Set default values for environment variables
ENV VLLM_HOME=/opt/vllm
ENV CUDA_HOME=/usr/local/cuda

WORKDIR $VLLM_HOME
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
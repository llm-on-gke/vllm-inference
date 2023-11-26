FROM nvcr.io/nvidia/pytorch:23.10-py3 AS dev

ENV VLLM_VERSION=1.0.0
ENV CUDA_VERSION=12.0.0
 
# Set default values for environment variables
ENV VLLM_HOME=/opt/vllm
ENV CUDA_HOME=/usr/local/cuda

WORKDIR $VLLM_HOME
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm
    
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
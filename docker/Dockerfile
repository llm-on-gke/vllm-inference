# Use the official CUDA 11.8 base image
FROM nvcr.io/nvidia/pytorch:22.12-py3


# Install vllm
RUN --mount=type=cache,target=/root/.cache/pip \
  torch==2.0.1+cu118, index_url="https://download.pytorch.org/whl/cu118"

RUN --mount=type=cache,target=/root/.cache/pip \
   pip install https://github.com/vllm-project/vllm/releases/download/v0.2.1/vllm-0.2.1-cp311-cp311-manylinux1_x86_64.whl
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install xformers==0.0.22

# Set the entrypoint command
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
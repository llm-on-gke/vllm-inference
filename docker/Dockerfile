FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubi8 AS dev

RUN apt-get update -y \
    && apt-get install -y python3-pip

WORKDIR /workspace
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
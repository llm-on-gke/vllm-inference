FROM nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu20.04 AS dev
RUN apt-get update -y \
    && apt-get install -y python3-pip

WORKDIR /.cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
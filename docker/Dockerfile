FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS dev

WORKDIR /.cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install vllm
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
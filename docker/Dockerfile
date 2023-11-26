FROM nvcr.io/nvidia/pytorch:23.04-py3 AS dev

RUN --mount=type=cache,target=/root/.cache/pip \
    pip -q install --upgrade fschat accelerate autoawq vllm
    
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
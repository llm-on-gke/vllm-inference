FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS dev


RUN --mount=type=cache,target=/root/.cache/pip \
    pip -q install --upgrade fschat accelerate autoawq vllm
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0 torchtext==0.16.0+cpu torchdata==0.7.0 --index-url https://download.pytorch.org/whl/cu121

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
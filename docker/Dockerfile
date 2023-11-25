FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
RUN --mount=type=cache,target=/root/.cache/pip \
   pip install https://github.com/vllm-project/vllm/releases/download/v0.2.2/vllm-0.2.2+cu118-cp310-cp310-manylinux1_x86_64.whl
RUN pip uninstall torch -y
RUN --mount=type=cache,target=/root/.cache/pip \
   pip install torch --upgrade --index-url https://download.pytorch.org/whl/cu118
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install xformers==0.0.22
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
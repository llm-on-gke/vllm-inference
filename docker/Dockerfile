FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

RUN pip install vllm
RUN pip install xformers==0.0.22

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.api_server"]
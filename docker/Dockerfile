# Use the official CUDA 11.8 base image
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Set environment variables for configuration
ENV VLLM_VERSION=1.0.0
ENV CUDA_VERSION=11.8

# Set default values for environment variables
ENV VLLM_HOME=/opt/vllm
ENV CUDA_HOME=/usr/local/cuda

# Set labels for better maintainability
#LABEL maintainer="Your Name <your.email@example.com>"
#LABEL description="Docker image for vllm with CUDA 11.8 for GPU"

# Install vllm
RUN apt-get update && apt-get install -y vllm

# Set the working directory
WORKDIR $VLLM_HOME

# Set the entrypoint command
ENTRYPOINT ["vllm"]
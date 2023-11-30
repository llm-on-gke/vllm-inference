# vllm-inference
vLLM vLLM is a fast and easy-to-use library for LLM inference and serving.

vLLM is fast with:

State-of-the-art serving throughput

Efficient management of attention key and value memory with PagedAttention

Continuous batching of incoming requests

Optimized CUDA kernels

## Opensource Models supported:
Llama2,Mistril, Falcon

## GKE Cluster and Nodepools
See the create-cluster.sh
Currently, there is issue running vLLM in GKE1.27, LLM models tested in GKE 1.26 only

## Deploy model to GKE cluster
See gke-deploy.yaml,

Notes: 
official container image: vllm/vllm-openai
Vertex vllm image: us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve

Huggingface token setup, 
Execute the command to deploy inference deployment in GKE, update the HF_TOKEN values
```
gcloud container clusters get-credentials llm-inference-l4 --location us-central1
export HF_TOKEN=<paste-your-own-token>
kubectl create secret generic huggingface --from-literal="HF_TOKEN=$HF_TOKEN" -n triton
```

## vLLM model parameters:
See this doc: https://docs.vllm.ai/en/latest/models/engine_args.html

You can adjust the model related parameters in args settings in gke-deploy.yaml 
--model=ModelNameFromHuggingFace
if you use Vertex image, you can set the Cloud Storage path of model, e.g., gs://vertex-model-garden-public-us-central1/llama2/llama2-13b-hf







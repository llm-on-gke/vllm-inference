# vllm-inference
vLLM is a fast and easy-to-use library for LLM inference and serving.

vLLM is fast with:

State-of-the-art serving throughput

Efficient management of attention key and value memory with PagedAttention

Continuous batching of incoming requests

Optimized CUDA kernels

vLLM has been used in Vertex AI Model Garden to deploy some Opensource LLM models

## Opensource Models supported
Llama2, Mistril, Falcon, see full list in https://docs.vllm.ai/en/latest/models/supported_models.html

## Prerequisite: Huggingface API token
Some models such as Llama2 will need Huggingface API token to download model files
Meta access request: https://ai.meta.com/resources/models-and-libraries/llama-downloads/ need regisgter an email address to download

Go to Hugging face, create account account with same email registered in Meta request. Then find Llama 2 model, fill out access request: https://huggingface.co/meta-llama/Llama-2-7b. Need to wait for a few hours with the approval email to be able to use Llama 2

Get Hugging face access token from HF settings,

## GKE Cluster and Nodepools
See the create-cluster.sh
### Quick Estimates of GPU type and number of GPU needed for model infereence:
Estimate the size of a model in gigabytes by multiplying the number of parameters (in billions) by 2. This approach is based on a simple formula: with each parameter using 16 bits (or 2 bytes) of memory in half-precision, the memory usage in GB is approximately twice the number of parameters. Therefore, a 7B parameter model, for instance, will take up approximately 14 GB of memory. We can comfortably run a 7B parameter model in Nvidia L4 and still have about 10 GB of memory remaining as a buffer for inferencing. Alternatively, you can choose to have 2 Tesla-T4 GPUs with 32G by sharding model across both GPUs, but there will be impacts of moving data around.  

For Models with larger parameter size, resource requirements can be reduced through weights Quantization into lower precision bits. 
Example, for Llama 2 70b model which may need 140G memeory with default half point(16 bits), resource requirements can be reduced with quatization into float 8 bits precision or even further with 4 bits, which only need 35G memory and can fit into 2 L4(48G)GPU. 
Reference: https://www.baseten.co/blog/llm-transformer-inference-guide/ 

### GKE Cluster
Currently, tested in GKE 1.26, up to GKE1.27.5.GKE.200 only, issues to test with some of latest versions. If you experience errors in logs: 
Can not find Nvidia driver, cuda initialization error. Then consider to switch to different GKE version may help resove the isssues.



The default shell script will create a private GKE cluster, if you prefer to use public cluster with easy access, then remove the following options   
  --enable-ip-alias \
  --enable-private-nodes  \
  --master-ipv4-cidr 172.16.0.32/28 \

### Nodepool
The default script for nodepool uses nvidia-l4 1 GPU as example, which uses us-central1,  region with following GPU related nodepool specs:

--accelerator type=nvidia-l4,count=1,gpu-driver-version=latest   --machine-type g2-standard-8 --node-version=1.27.5.GKE.200

Alternatively, you can choose to use 2 TESLA-T4 GPU which can be us-west1 with tweaks to the nodepool specs:
--accelerator type=nvidia-tesla-t4,count=2,gpu-driver-version=latest   --machine-type n1-standard-8 --node-version=1.27.5.GKE.200

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
This GEK huggingface secrect is used to set the environment value in gke-deploy.yaml( need to keep the name: HUGGING_FACE_HUB_TOKEN ):
env:
    - name: HUGGING_FACE_HUB_TOKEN
      valueFrom:
            secretKeyRef:
              name: huggingface
              key: HF_TOKEN


## vLLM model config parameters:
Update vllm-deploy.yml file, 

You can override the command and arguments, 

if you prefer to Langchain and OpenAI integration in applications, you can use this:

command: ["python3", "-m", "vllm.entrypoints.openai.api_server"]

or you can use different entrypoint for native vLLM APIs:

command: ["python3", "-m", "vllm.entrypoints.api_server"]

To understand the vLLM model related arguments, See this doc: https://docs.vllm.ai/en/latest/models/engine_args.html

You can adjust the model related parameters in args settings in gke-deploy.yaml 

--model=ModelNameFromHuggingFace, replace with specific models from Huggingface, meta-llama/Llama-2-7b-hf, meta-llama/Llama-2-13b-hf, mistralai/Mistral-7B-v0.1, tiiuae/falcon-7b

If you use Vertex vLLM image, --model value you can be full Cloud Storage path of model files, e.g., gs://vertex-model-garden-public-us-central1/llama2/llama2-13b-hf

## Deploy the model to GKE
After vllm-deploy.yaml file been updated with proper settings, execute the followin command:
```
kubectl apply -f vllm-deploy.yaml -n NamespaceName   
```
The following GKE artifacts will be created:
a. vllm-server deployment
b. Ingress
b. Service with endpoint of LLM APIs, routing traffic through Ingress


## Tests

Simple way: 
kubectl get service/vllm-server -o jsonpath='{.spec.clusterIP}' -n triton

Then use the following curl command to test inside the Cluster:
curl http://ClusterIP:8000/v1/models

curl http://ClusterIP:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-2-7b-hf",
        "prompt": "San Francisco is a",
        "max_tokens": 250,
        "temperature": 0.1
    }'


## Deploy WebApp

Siince vLLM can expose different model as OpenAI style APIs, different models will be transparent applications how to access LLM models.  

The sample app provided will use vLLM OpenAI library to initialize any model deployed through vLLM:
```
import gradio as gr
import requests
import os
from langchain.llms import VLLMOpenAI
llm_url = os.environ.get('LLM_URL')
llm_name= os.environ.get('LLM_NAME')
llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base=f"{llm_url}/v1",
    model_name=f"{llm_name}",
    model_kwargs={"stop": ["."]},
)
```
After that, you can use any other Langchain related libraries

You need to build the webapp image:
update the cloudbuild.yaml file under webapp directory, 
then run the build
```
cd webapp
gcloud builds submit. 
```

Then update the vllm-client.yaml file, 
a. image: URI, replace with your own vllm-client image
b. LLM server and name settings:
 - name: LLM_URL
            value: "http://CLusterIP:8000"   (replace with the full LLM svc endpoint including port)
- name: LLM_NAME
            value: "meta-llama/Llama-2-7b-hf"  ( replace with your own Model setup earlier)

Run the command to deploy webapp, 
kubectl apply -f vllm-client.yaml -n triton
kubectl get service/vllm-client -o jsonpath='{.spec.externalIP}' -n triton

## Validations:

Go to the external IP for the webapp, hptt://externalIP:8080, 
and test a few questions.  





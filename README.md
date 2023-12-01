# vllm-inference
vLLM is a fast and easy-to-use library for LLM inference and serving.

vLLM is fast with:

State-of-the-art serving throughput

Efficient management of attention key and value memory with PagedAttention

Continuous batching of incoming requests

Optimized CUDA kernels

## Opensource Models supported:
Llama2, Mistril, Falcon, see full list in https://docs.vllm.ai/en/latest/models/supported_models.html

## GKE Cluster and Nodepools
See the create-cluster.sh
Currently, tested in GKE 1.26, up to GKE1.27.5.GKE.200 only, issues to test with some of latest versions. If you experience errors in logs: 
Can not find Nvidia driver, cuda initialization error. Then consider to switch to different GKE version may help resove the isssues

The default script uses tesla-l4 1 GPU as example, which uses us-central1 region with following GPU related nodepool specs:

--accelerator type=nvidia-l4,count=1,gpu-driver-version=latest   --machine-type g2-standard-8 --node-version=1.27.5.GKE.200

You can choose to use 2 TESLA-T4 GPU with tweaks to the nodepool specs:
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


## vLLM model parameters:
See this doc: https://docs.vllm.ai/en/latest/models/engine_args.html

You can adjust the model related parameters in args settings in gke-deploy.yaml 
--model=ModelNameFromHuggingFace
if you use Vertex image, you can set the Cloud Storage path of model, e.g., gs://vertex-model-garden-public-us-central1/llama2/llama2-13b-hf

## Tests

Simple way: 
kubectl get service/vllm-server -o jsonpath='{.spec.clusterIP}' -n triton

Then use the following curl command to test:
curl http://ClusterIP:8000/generate \
    -d '{
        "prompt": "San Francisco is a",
        "use_beam_search": true,
        "n": 4,
        "temperature": 0
    }'







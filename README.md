# Serving Open Source LLMs on GKE using vLLM framework

This post shows how to serve Open source LLM models(Mistrial 7B, Llama2 etc) on Nvidia GPUs(L4, Tesla-T4, for example) running on Google Cloud Kubernetes Engine (GKE). It will help you understand the AI/ML ready features of GKE and how to use them to serve large language models make life of self-managing OSS LLM models in GKE not as dauting as you may originally think of .


TGI and vLLM are 2 common frameworks to address significant challenges on slow latencities to obtain an output from a LLM, primarily due to ever increasing LLM substantial sizes to get responses back  

𝐯𝐋𝐋𝐌(𝐕𝐞𝐫𝐬𝐚𝐭𝐢𝐥𝐞 𝐥𝐚𝐫𝐠𝐞 𝐥𝐚𝐧𝐠𝐮𝐚𝐠𝐞 𝐦𝐨𝐝𝐞𝐥) is a framework designed to enhance the inference and serving speed of LLMs. It has demonstrated remarkable performance improvements compared to mainstream frameworks like Hugging Face’s Transformers, primarily because of a highly innovative new algorithm at its core.

One key reason behind vLLM’s speed during inference is its use of the 𝐏𝐚𝐠𝐞𝐝 𝐀𝐭𝐭𝐞𝐧𝐭𝐢𝐨𝐧 𝐭𝐞𝐜𝐡𝐧𝐢𝐪𝐮𝐞. In traditional attention mechanisms, the keys and values computed are stored in GPU memory as a KV cache. This cache stores attention keys and values for previous tokens, which can consume a significant amount of memory, especially for large models and long sequences. These keys and values are also stored in a contiguous manner. 

𝐓𝐆𝐈 (𝐓𝐞𝐱𝐭-𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧-𝐈𝐧𝐟𝐞𝐫𝐞𝐧𝐜𝐞) is another solution aimed at increasing the speed of LLM inference. It offers high-performance text generation using Tensor Parallelism and dynamic batching for popular open-source LLMs like StarCoder, BLOOM,Llama and other models.

𝐓𝐆𝐈 𝐯𝐬 𝐯𝐋𝐋𝐌

- TGI does not support paged optimization.

-Both techniques don’t handle all LLM architectures.

-TGI also allows quantizing and fine-tuning models, which are not supported by vLLM.

-VLLM achieves better performance than TGI and the Hugging Face transformer library, with up to 24x higher throughput compared to Hugging Face and up to 3.5x higher throughput than TGI.
This post shows how to serve OSS LLMs(Mistral 7B, or Llama2) model on L4 GPUs running on Google Cloud Kubernetes Engine (GKE). It will help you understand the AI/ML ready features of GKE and how to use them to serve large language models.


GKE is a fully managed service that allows you to run containerized workloads on Google Cloud. It’s a great choice for running large language models and AI/ML workloads because it is easy to set up, it’s secure, and it’s AI/ML batteries included. GKE installs the latest NVIDIA GPU drivers for you in GPU-enabled node pools, and gives you autoscaling and partitioning capabilities for GPUs out of the box, so you can easily scale your workloads to the size you need while keeping the costs under control. 


For example on how to serve Open source model( Mistral 7B) on GKE using TGI, please refer to this Google community blog:
https://medium.com/google-cloud/serving-mistral-7b-on-l4-gpus-running-on-gke-25c6041dff27


## Opensource Models supported
Llama2, Mistril, Falcon, see full list in https://docs.vllm.ai/en/latest/models/supported_models.html

## Prerequisite: Huggingface API token

Access to a Google Cloud project with the L4 GPUs available and enough quota in the region you select.
A computer terminal with kubectl and the Google Cloud SDK installed. From the GCP project console you’ll be working with, you may want to use the included Cloud Shell as it already has the required tools installed.
Some models such as Llama2 will need Huggingface API token to download model files
Meta access request: https://ai.meta.com/resources/models-and-libraries/llama-downloads/ need regisgter an email address to download

Go to Hugging face, create account account with same email registered in Meta request. Then find Llama 2 model, fill out access request: https://huggingface.co/meta-llama/Llama-2-7b. Need to wait for a few hours with the approval email to be able to use Llama 2

Get Hugging face access token from your huggingface account profile settings,

## Setup project environments

From your console, select the Google Cloud region and project, checking that there’s availability for L4 GPUs in the one that you end up selecting. The one used in this tutorial is us-central, where at the time of writing this article there was availability for L4 GPUs( alternatively, you can choose other regions with different GPU accelerator type available):

```
export PROJECT_ID=<your-project-id>
export REGION=us-central1
export ZONE_1=${REGION}-a # You may want to change the zone letter based on the region you selected above
export ZONE_2=${REGION}-b # You may want to change the zone letter based on the region you selected above
export CLUSTER_NAME=vllm-serving-cluster
export NAMESPACE=vllm
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE_1"
```
Then, enable the required APIs to create a GK cluster:
```
gcloud services enable compute.googleapis.com container.googleapis.com
```

Also, you may go ahead download the source code repo for this exercise, :
```
git clone https://github.com/llm-on-gke/vllm-inference.git
cd vllm-inference
```


In this exercise, you will be using the default service account to create the cluster, you need to grant it the required permissions to store metrics and logs in Cloud Monitoring that you will be using later on:

```
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
GCE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for role in monitoring.metricWriter stackdriver.resourceMetadata.writer; do
  gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:${GCE_SA} --role=roles/${role}
done
```
## Create GKE Cluster and Nodepools

### Quick Estimates of GPU type and number of GPU needed for model infereence:
Estimate the size of a model in gigabytes by multiplying the number of parameters (in billions) by 2. This approach is based on a simple formula: with each parameter using 16 bits (or 2 bytes) of memory in half-precision, the memory usage in GB is approximately twice the number of parameters. Therefore, a 7B parameter model, for instance, will take up approximately 14 GB of memory. We can comfortably run a 7B parameter model in Nvidia L4 and still have about 10 GB of memory remaining as a buffer for inferencing. Alternatively, you can choose to have 2 Tesla-T4 GPUs with 32G by sharding model across both GPUs, but there will be impacts of moving data around.  

For Models with larger parameter size, resource requirements can be reduced through weights Quantization into lower precision bits. 
Example, for Llama 2 70b model which may need 140G memeory with default half point(16 bits), resource requirements can be reduced with quatization into float 8 bits precision or even further with 4 bits, which only need 35G memory and can fit into 2 L4(48G)GPU. 
Reference: https://www.baseten.co/blog/llm-transformer-inference-guide/ 

### GKE Cluster

Now, create a GKE cluster with a minimal default node pool, as you will be adding a node pool with L4 GPUs later on:
```
gcloud container clusters create $CLUSTER_NAME \
  --location "$REGION" \
  --workload-pool "${PROJECT_ID}.svc.id.goog" \
  --enable-image-streaming --enable-shielded-nodes \
  --shielded-secure-boot --shielded-integrity-monitoring \
  --enable-ip-alias \
  --node-locations="$ZONE_1" \
  --workload-pool="${PROJECT_ID}.svc.id.goog" \
  --addons GcsFuseCsiDriver   \
  --no-enable-master-authorized-networks \
  --machine-type n2d-standard-4 \
  --num-nodes 1 --min-nodes 1 --max-nodes 5 \
  --ephemeral-storage-local-ssd=count=2 \
  --enable-ip-alias
```

### Nodepool

Create an additional Spot node pool with regular (we use spot to illustrate) VMs with 2 L4 GPUs each:
```
gcloud container node-pools create g2-standard-24 --cluster $CLUSTER_NAME \
  --accelerator type=nvidia-l4,count=1,gpu-driver-version=latest \
  --machine-type g2-standard-8 \
  --ephemeral-storage-local-ssd=count=1 \
  --enable-autoscaling --enable-image-streaming \
  --num-nodes=1 --min-nodes=0 --max-nodes=2 \
  --shielded-secure-boot \
  --shielded-integrity-monitoring \
  --node-locations $ZONE_1,$ZONE_2 --region $REGION --spot
```
Note how easy enabling GPUs in GKE is. Just adding the option --accelerator automatically bootstraps the nodes with the necessary drivers and configuration so your workloads can start using the GPUs attached to the cluster nodes. If you need to try tesla-t4, need to update  --accelerator and --machine-type parameter values, as one example:
--accelerator type=nvidia-tesla-t4,count=1,gpu-driver-version=latest
machine-type n2d-standard-8

After a few minutes, check that the node pool was created correctly:
```
gcloud container node-pools list --region $REGION --cluster $CLUSTER_NAME
```

Also, check that the corresponding nodes in the g2-standard-24 node pool have the GPUs available:
```
kubectl get nodes -o json | jq -r '.items[] | {name:.metadata.name, gpus:.status.capacity."nvidia.com/gpu"}'
```
You should get one with 2 GPUs available corresponding to the node pool you just created:

{
  "name": "vllm-serving-cluster-g2-standard-8-XXXXXX",
  "gpus": "1"
}

Run the following commands to setup identiy and IAM roles:
```
kubectl create ns $NAMESPACE
kubectl create serviceaccount $NAMESPACE --namespace $NAMESPACE
gcloud iam service-accounts add-iam-policy-binding $GCE_SA \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/${NAMESPACE}]"

kubectl annotate serviceaccount $NAMESPACE \
    --namespace $NAMESPACE \
    iam.gke.io/gcp-service-account=$GCE_SA
```

## Deploy model to GKE cluster
We’re now ready to deploy the model. 
Save the following vllm-deploy.yaml,
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
  labels:
    app: vllm-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-inference-server
  template:
    metadata:
      labels:
        app: vllm-inference-server
    spec:
      volumes:
       - name: cache
         emptyDir: {}
       - name: dshm
         emptyDir:
              medium: Memory
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-l4
      serviceAccountName: triton
      containers:
        - name: vllm-inference-server
          image: vllm/vllm-openai
          imagePullPolicy: IfNotPresent

          resources:
            limits:
              nvidia.com/gpu: 1
          env:
            - name: HUGGING_FACE_HUB_TOKEN
              valueFrom:
                secretKeyRef:
                  name: huggingface
                  key: HF_TOKEN
            - name: TRANSFORMERS_CACHE
              value: /.cache
            - name: shm-size
              value: 1g
          command: ["python3", "-m", "vllm.entrypoints.openai.api_server"]
          args: ["--model=meta-llama/Llama-2-7b-hf",
                 "--gpu-memory-utilization=0.95",
                 "--disable-log-requests",
                 "--trust-remote-code",
                 "--port=8000",
                 "--tensor-parallel-size=1"]
          ports:
            - containerPort: 8000
              name: http
          securityContext:
            runAsUser: 1000
          volumeMounts:
            - mountPath: /dev/shm
              name: dshm
            - mountPath: /.cache
              name: cache

---
apiVersion: v1
kind: Service
metadata:
  name: vllm-inference-server
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
  labels:
    app: vllm-inference-server   
spec:
  type: NodePort
  ports:
    - port: 8000
      targetPort: http
      name: http-inference-server
    
  selector:
    app: vllm-inference-server

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vllm-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "ingress-vllm"
spec:
  rules:
  - http:
      paths:
      - path: "/"
        pathType: Prefix
        backend:
          service:
            name: vllm-inference-server
            port:
              number: 8000
```            


Notes: 
We include kubernetes resource templates for a deployment, service, and Ingress
We use official container image to run the modles: vllm/vllm-openai
Huggingface token setup, 
Execute the command to deploy inference deployment in GKE, update the HF_TOKEN values

```
gcloud container clusters get-credentials $CLUSTER_NAME $REGION
export HF_TOKEN=<paste-your-own-token>
kubectl create secret generic huggingface --from-literal="HF_TOKEN=$HF_TOKEN" -n $NAMESPACE
```
This GKE huggingface secrect is used to set the environment value in gke-deploy.yaml( need to keep the name: HUGGING_FACE_HUB_TOKEN ):
env:
    - name: HUGGING_FACE_HUB_TOKEN
      valueFrom:
            secretKeyRef:
              name: huggingface
              key: HF_TOKEN


## vLLM model config parameters:
Update vllm-deploy.yml file as described earlier, 

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
kubectl apply -f vllm-deploy.yaml -n $NAMESPACE 
```
The following GKE artifacts will be created:
a. vllm-server deployment
b. Ingress
b. Service with endpoint of LLM APIs, routing traffic through Ingress

Check all the objects you’ve just created:

kubectl get all
Check that the pod has been correctly scheduled in one of the nodes in the g2-standard-8 node pool that has the GPUs available:


## Tests

Simplely run the following command to get the cluster ip:
```
kubectl get service/vllm-server -o jsonpath='{.spec.clusterIP}' -n $NAMESPACE
```

Then use the following curl command to test inside the Cluster(update the cluster IP first):
```
kubectl run curl --image=curlimages/curl \
    -it --rm --restart=Never \
    -- "$CLUSTERIP:8000/v1/models" 

curl http://ClusterIP:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "google/gemma-1.1-2b-it",
        "prompt": "San Francisco is a",
        "max_tokens": 250,
        "temperature": 0.1
    }'
```

## Deploy WebApp

Siince vLLM can expose different model as OpenAI style APIs, different models will be transparent applications how to access LLM models.  

The sample app provided will use vLLM OpenAI library to initialize any model deployed through vLLM with following python code:

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

Note, you don't need to run this code here.

You need to build the webapp container image first so that you can host the webapp in Cloud Run:
update(don't run it) the cloudbuild.yaml file under webapp directory to replace your own artifactory repository paths, 

steps:
- name: 'gcr.io/cloud-builders/docker'
  args: [ 'build', '-t', 'us-east1-docker.pkg.dev/$PROJECT_ID/gke-llm/vllm-client:latest', '.' ]
images:
- 'us-east1-docker.pkg.dev/$PROJECT_ID/gke-llm/vllm-client:latest'


then run the build to build sample app container image use Cloud Build:

```
cd webapp
gcloud builds submit. 
```

Then update the vllm-client.yaml file, 
 - name: gradio
        image: us-east1-docker.pkg.dev/PROJECT_ID/gke-llm/vllm-client:latest
        env:
          - name: LLM_URL
            value: "http://CLusterIP:8000"
          - name: LLM_NAME
            value: "meta-llama/Llama-2-7b-hf"

a. image: URI, replace with your own vllm-client image
b. LLM server and name settings:
 - name: LLM_URL
            value: "http://CLusterIP:8000"   (replace with the full LLM svc endpoint including port)
- name: LLM_NAME
            value: "meta-llama/Llama-2-7b-hf"  ( replace with your own Model setup earlier)

Run the command to deploy webapp, 
kubectl apply -f vllm-client.yaml -n $NAMESPACE
kubectl get service/vllm-client -o jsonpath='{.spec.externalIP}' -n $NAMESPACE

## Validations:

Go to the external IP for the webapp, hptt://externalIP:8080, 
and test a few questions from the web application.  

## Cleanups:
Don’t forget to clean up the resources created in this article once you’ve finished experimenting with GKE and Mistral 7b, as keeping the cluster running for a long time can incur in important costs. To clean up, you just need to delete the GKE cluster:

gcloud container clusters delete $CLUSTER_NAME — region $REGION

## Conclusion
This post tries to demonstrate how deploying Opensource LLM models such as Mistrial 7B and Llama2 7B/13B using vLLM on GKE is flexible and straightforward. 
LLM operations and self manage AI ML workload in  flagship Managed kubernates platform GKE enables deploying LLM models in production, bringing ML Ops one step closer to existing platform teams with expertises in those managed platforms. Also, given the resources that are consumed, and the number of potential applications using AI/ML features moving forward, having a framework that offers scalability and cost control features simplifies adoption.

Don't forget to check out other GKE related resources on AI ML infrastrucure offered by Google Cloud. 



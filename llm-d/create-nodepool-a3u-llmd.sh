gcloud container node-pools create a3-ultra-rdma-pool \
    --cluster=warm-a3u-us1b \
    --project=samskillman-hpc-benchmarks \
    --location=us-south1-b \
    --machine-type=a3-ultragpu-8g \
    --accelerator=type=nvidia-h200-141gb,count=8,gpu-driver-version=disabled \
    --image-type=UBUNTU_CONTAINERD \
    --disk-type=hyperdisk-balanced \
    --gateway-api=standard \
    --disk-size=25 \
    --num-nodes=1 \
    --spot \
    --additional-node-network="network=warm-a3u-us1b-net-1,subnetwork=warm-a3u-us1b-sub-1" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-0" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-1" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-2" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-3" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-4" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-5" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-6" \
    --additional-node-network="network=warm-a3u-us1b-rdma-net,subnetwork=warm-a3u-us1b-rdma-sub-7"

kubectl create secret generic llm-d-hf-token --from-literal=HF_TOKEN="${HF_TOKEN}"


# Inference Gateway API CRDs
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api-inference-extension/raw/v1.4.0/config/crd/bases/inference.networking.x-k8s.io_inferenceobjectives.yaml


# Example: Apply Prometheus Operator manifests to install ServiceMonitor CRD
kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/latest/download/bundle.yaml
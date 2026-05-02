gcloud container node-pools create ubuntu-b200-580   --location us-west8-c   --node-locations=us-west8-c   --spot   --machine-type a4-highgpu-8g   --accelerator "type=nvidia-b200,count=8,gpu-driver-version=disabled"   --num-nodes=1   --cluster warm-a4-uw8c   --node-version=1.35   --image-type "UBUNTU_CONTAINERD" 

kubectl apply -f daemonset-preload-R580.yaml



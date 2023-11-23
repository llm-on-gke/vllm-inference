git clone https://github.com/vllm-project/vllm
cd vllm
cp ../cloudbuild.yaml .
cp ../Dockerfile .
gcloud builds submit .
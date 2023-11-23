git clone https://github.com/vllm-project/vllm
cp cloudbuild.yaml vllm
cp Dockerfile vllm
gcloud builds submit .
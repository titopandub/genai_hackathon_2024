MODEL_ID="textembedding-gecko-multilingual"
PROJECT_ID="328583281153"
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl \
-X POST \
-H "Authorization: Bearer ${ACCESS_TOKEN}" \
-H "Content-Type: application/json" \
https://asia-southeast1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/publishers/google/models/${MODEL_ID}:predict -d \
'{
  "instances": [
    { "content": "What is life?"}
  ],
}'
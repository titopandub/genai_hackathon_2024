PROJECT_ID=vidio-quiz-prod
LOCATION=asia-southeast1
ACCELERATOR_TYPE=NVIDIA_TESLA_T4
# LOCATION=us-central1
# ACCELERATOR_TYPE=NVIDIA_TESLA_V100
BASE_MODEL_VERSION_ID=textembedding-gecko-multilingual@001
PIPELINE_SCRATCH_PATH=gs://genai_hackathon_2024/data/fine_tuning_text_embedding/output/
QUERIES_PATH=gs://genai_hackathon_2024/data/fine_tuning_text_embedding/20240313_1044_query.json
CORPUS_PATH=gs://genai_hackathon_2024/data/fine_tuning_text_embedding/20240313_1044_corpus.json
TRAIN_LABEL_PATH=gs://genai_hackathon_2024/data/fine_tuning_text_embedding/20240313_1044_train.tsv
TEST_LABEL_PATH=gs://genai_hackathon_2024/data/fine_tuning_text_embedding/20240313_1044_test.tsv
BATCH_SIZE=64
ITERATIONS=400


curl -X POST  \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
"https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/pipelineJobs?pipelineJobId=tune-text-embedding-$(date +%Y%m%d%H%M%S)" \
-d '{
  "displayName": "tune-text-embedding-model",
  "runtimeConfig": {
    "gcsOutputDirectory": "'${PIPELINE_SCRATCH_PATH}'",
    "parameterValues": {
      "project":  "'${PROJECT_ID}'",
      "base_model_version_id":  "'${BASE_MODEL_VERSION_ID}'",
      "location": "'${LOCATION}'",
      "queries_path":  "'${QUERIES_PATH}'",
      "corpus_path":  "'${CORPUS_PATH}'",
      "train_label_path":  "'${TRAIN_LABEL_PATH}'",
      "test_label_path":  "'${TEST_LABEL_PATH}'",
      "batch_size":  "'${BATCH_SIZE}'",
      "iterations":  "'${ITERATIONS}'",
      "accelerator_type": "'${ACCELERATOR_TYPE}'"
    }
  },
  "templateUri": "https://us-kfp.pkg.dev/ml-pipeline/llm-text-embedding/tune-text-embedding-model/v1.1.1"
}'
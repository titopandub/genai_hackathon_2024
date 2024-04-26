from vertexai.language_models import TextEmbeddingModel
import src.lib.datadog_statsd as statsd
from ddtrace import tracer
from google.cloud import aiplatform
from abc import abstractmethod
from src.config import config

class Embedding:
    @abstractmethod
    def embedding_text(self, text):
        pass

class PretrainEmbedding(Embedding):
    def __init__(self, model) -> None:
        self.model = model

    @tracer.wrap(name="embedding",resource="embed")
    def embedding_text(self, text): 
        statsd.increment('vidibot.embedding_count', tags=["environment:prod"])
        prediction = self.model.predict(instances=[{
            "content": text,
            "task_type": "DEFAULT",
            "title": ""
        }])
        for embedding in prediction.predictions:
            vector = embedding
        return vector

class GoogleEmbedding(Embedding):
    def __init__(self, model) -> None:
        self.model = model

    @tracer.wrap(name="embedding",resource="embed")
    def embedding_text(self, text): 
        statsd.increment('vidibot.embedding_count', tags=["environment:prod"])
        embeddings = self.model.get_embeddings([text])
        for embedding in embeddings:
            vector = embedding.values
        return vector

aiplatform.init(
    project=config['aiplatform']['project'],
    location=config['aiplatform']['location'],
    staging_bucket=config['aiplatform']['staging_bucket'],
)
google_model = TextEmbeddingModel.from_pretrained("textembedding-gecko-multilingual")
pretrain_model = aiplatform.Endpoint(config['embedding']['pretrain_model_id'])
# embedding_model = pretrain_model
embedding_model = google_model

# embedding = PretrainEmbedding(embedding_model)
embedding = GoogleEmbedding(embedding_model)
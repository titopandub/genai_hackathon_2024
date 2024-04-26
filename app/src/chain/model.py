
from langchain_google_vertexai import VertexAI
from src.config import config

model = VertexAI(model_name="gemini-pro", project=config["vertexai"]["project"], location="asia-southeast1", temperature=0.4)
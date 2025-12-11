# # infrastructure/hf_embedding_adapter.py
# from sentence_transformers import SentenceTransformer

# class HFEmbeddingProvider:
#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         self.model = SentenceTransformer(model_name)

#     def embed(self, text: str):
#         """
#         Accepts a string and returns a list[float] embedding.
#         """
#         # model.encode returns numpy array — convert to list for Chroma compatibility
#         emb = self.model.encode(text, show_progress_bar=False)
#         return emb.tolist()

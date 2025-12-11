# # application/ingestion.py

# import uuid
# from core.entities import DocumentChunk


# def split_into_chunks(text, chunk_size=500):
#     words = text.split()
#     chunks = []
#     current_chunk = []

#     for word in words:
#         current_chunk.append(word)
#         if len(current_chunk) >= chunk_size:
#             chunks.append(" ".join(current_chunk))
#             current_chunk = []

#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks


# def ingest_document(url, loader, vector_store):
#     text = loader.load(url)
#     chunks = split_into_chunks(text)

#     embedding_chunks = []
#     for chunk in chunks:
#         embedding = vector_store.embed_fn(chunk)["embedding"]
#         embedding_chunks.append(
#             DocumentChunk(id=str(uuid.uuid4()), text=chunk, embedding=embedding)
#         )

#     vector_store.add_chunks(embedding_chunks)

import chromadb

class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.Client()

        # Delete existing collection if present
        try:
            self.client.delete_collection("docs")
        except Exception:
            pass  # ignore if it doesn't exist

        # Create fresh collection
        self.collection = self.client.create_collection(
            name="docs",
            metadata={"hnsw:space": "cosine"}
        )

        self.raw_text = ""

    def add_documents(self, docs):
        for i, doc in enumerate(docs):
            self.collection.add(
                documents=[doc],
                ids=[str(i)]
            )

    def search(self, query, k=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        return results["documents"][0] if results["documents"] else []

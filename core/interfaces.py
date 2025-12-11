# # core/interfaces.py

# from abc import ABC, abstractmethod
# from typing import List
# from core.entities import DocumentChunk, ChatMessage


# class VectorStore(ABC):

#     @abstractmethod
#     def add_chunks(self, chunks: List[DocumentChunk]):
#         pass

#     @abstractmethod
#     def search(self, query: str, top_k: int):
#         pass


# class LLMProvider(ABC):

#     @abstractmethod
#     def generate_answer(self, question: str, context: str, chat_history: List[ChatMessage]) -> str:
#         pass

#     @abstractmethod
#     def embed(self, text: str) -> list:
#         pass

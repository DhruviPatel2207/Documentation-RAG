# # application/rag_graph.py

# from core.entities import ChatMessage


# class RAGGraph:

#     def __init__(self, vector_store, llm_provider):
#         self.vector_store = vector_store
#         self.llm = llm_provider

#     def ask(self, question, chat_history):

#         # Step 1 – Retrieve context
#         retrieved_docs = self.vector_store.search(question, top_k=3)
#         context = "\n\n".join(retrieved_docs)

#         # Step 2 – Generate LLM Answer
#         answer = self.llm.generate_answer(question, context, chat_history)

#         # Step 3 – Update chat history
#         chat_history.append(ChatMessage(role="user", content=question))
#         chat_history.append(ChatMessage(role="assistant", content=answer))

#         return {
#             "answer": answer,
#             "chat_history": chat_history
#         }

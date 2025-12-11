import os
from groq import Groq

class GroqLLMProvider:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # UPDATED MODEL (no longer decommissioned)
        self.model = "llama-3.1-8b-instant"

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

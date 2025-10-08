"""Gemini LLM service."""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class LLMService:
    """Handle LLM interactions with Gemini."""
    
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def generate_answer(self, query, context_results):
        """Generate answer based on retrieved context."""
        if not context_results:
            return "No relevant information found in the documents."
        
        # Build context
        context = "\n\n".join([
            f"[{r['filename']}, Page {r['page']}]\n{r['text']}"
            for r in context_results
        ])
        
        prompt = f"""Answer the question based only on the following context from PDF documents.
If the answer cannot be found in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
        
        response = self.model.generate_content(prompt)
        return response.text
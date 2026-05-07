import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MediSearch AI, a medical research assistant. Your role is to provide accurate, evidence-based answers grounded in the provided research context.

Rules:
- Base your answer ONLY on the provided context. Do not use prior knowledge.
- Cite sources using [Source N] notation matching the source numbers provided.
- If the context is insufficient, clearly state what information is missing.
- Be concise but thorough. Use medical terminology appropriately.
- Include relevant statistics, findings, or conclusions from the sources.
- Never fabricate citations or make unsupported claims."""


def build_context_prompt(query: str, documents: list[dict], history: list[dict] | None = None) -> list[dict]:
    context_parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.get("metadata", {})
        header = f"[Source {i}] {meta.get('title', 'Unknown')} ({meta.get('journal', '')}, {meta.get('year', '')})"
        context_parts.append(f"{header}\n{doc['text']}")

    context_block = "\n\n---\n\n".join(context_parts)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

    user_message = f"Research Context:\n{context_block}\n\nQuestion: {query}"
    messages.append({"role": "user", "content": user_message})

    return messages


class LLMClient:
    def __init__(self):
        self.settings = get_settings()

    def generate(
        self,
        query: str,
        documents: list[dict],
        history: list[dict] | None = None,
    ) -> str:
        messages = build_context_prompt(query, documents, history)

        if self.settings.use_groq:
            return self._generate_groq(messages)
        return self._generate_ollama(messages)

    def _generate_groq(self, messages: list[dict]) -> str:
        from groq import Groq

        try:
            client = Groq(api_key=self.settings.groq_api_key)
            response = client.chat.completions.create(
                model=self.settings.groq_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise RuntimeError(f"Groq API error: {e}")

    def _generate_ollama(self, messages: list[dict]) -> str:
        import ollama

        try:
            response = ollama.chat(
                model=self.settings.ollama_model, messages=messages
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(
                f"Failed to generate response. Ensure Ollama is running with model '{self.settings.ollama_model}'. Error: {e}"
            )

    def is_available(self) -> bool:
        if self.settings.use_groq:
            try:
                from groq import Groq

                client = Groq(api_key=self.settings.groq_api_key)
                client.models.list()
                return True
            except Exception:
                return False
        else:
            try:
                import ollama

                ollama.list()
                return True
            except Exception:
                return False

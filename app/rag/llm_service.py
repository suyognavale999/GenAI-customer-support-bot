from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import ApplicationException


class LLMService:

    def __init__(self):
        if settings.llm_base_url:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
        else:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
            )

    def generate_answer(self, question, context):

        if not settings.llm_api_key:
            raise ApplicationException(
                message="LLM API key is not configured.",
                status_code=503,
                error_code="LLM_NOT_CONFIGURED",
            )

        if not settings.llm_model:
            raise ApplicationException(
                message="LLM model is not configured.",
                status_code=503,
                error_code="LLM_MODEL_NOT_CONFIGURED",
            )

        system_prompt = (
            "You are a document-based customer support assistant.\n\n"
            "Answer only from the supplied document context.\n\n"
            "Rules:\n"
            "1. Do not invent information.\n"
            "2. Give clear, practical, and concise answers.\n"
            "3. Preserve technical terms, commands, and names.\n"
            "4. Never expose passwords, API keys, or secrets.\n"
            "5. If the context is insufficient, say that the "
            "uploaded documents do not contain enough information."
        )

        user_prompt = (
            "DOCUMENT CONTEXT:\n\n"
            + context
            + "\n\nUSER QUESTION:\n\n"
            + question
        )
        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            )

            answer = response.choices[0].message.content

            if not answer:
                raise ValueError("The LLM returned an empty response.")

            return answer.strip()

        except ApplicationException:
            raise

        except Exception as exception:
            raise ApplicationException(
                message="Unable to generate the answer.",
                status_code=502,
                error_code="LLM_REQUEST_FAILED",
            ) from exception

from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import ApplicationException

import logging

logger = logging.getLogger(__name__)


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
        
        if context:
            system_prompt = (
                "You are a document-based customer support assistant.\n"
                "Answer from the supplied document context.\n"
                "Do not invent information.\n"
                "Return well-structured plain text.\n"
                "Use headings and numbered points where appropriate.\n"
                "Do not use Markdown symbols such as *, **, ###, or backticks."
            )

            user_prompt = (
                "DOCUMENT CONTEXT:\n\n"
                + context
                + "\n\nUSER QUESTION:\n\n"
                + question
            )
        else:
            system_prompt = (
                "You are a helpful AI assistant.\n"
                "Answer general questions using your knowledge.\n"
                "Give clear, concise, and well-structured answers.\n"
                "Do not use Markdown symbols such as *, **, ###, or backticks."
            )

            user_prompt = question
        
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
            logger.exception(
                "LLM request failed: model=%s, base_url=%s, error=%s",
                settings.llm_model,
                settings.llm_base_url,
                str(exception),
            )

            raise ApplicationException(
                message="Unable to generate the answer.",
                status_code=502,
                error_code="LLM_REQUEST_FAILED",
            ) from exception

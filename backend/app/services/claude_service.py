"""Claude API integration service.

Wraps the Anthropic Python SDK to provide a clean, typed interface
for generating AI responses to cloud/IT consulting questions.
"""

import logging
from dataclasses import dataclass

import anthropic

from app.config import Settings
from app.exceptions import ClaudeAPIError, ClaudeRateLimitError
from app.prompts.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class ClaudeResponse:
    """Typed response returned by the Claude service.

    Attributes:
        content: The generated response text (markdown).
        model: The model ID that produced the response.
        input_tokens: Number of tokens in the prompt.
        output_tokens: Number of tokens in the response.
    """

    content: str
    model: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed by this request."""
        return self.input_tokens + self.output_tokens


class ClaudeService:
    """Service for interacting with Anthropic's Claude API.

    Handles prompt construction, API communication, error mapping,
    and response normalisation.

    Attributes:
        _client: The Anthropic SDK client instance.
        _model: The Claude model identifier to use.
        _max_tokens: Maximum tokens allowed in the response.
        _temperature: Sampling temperature (0.0 – 1.0).
    """

    def __init__(self, settings: Settings) -> None:
        """Initialise the Claude service with application settings.

        Args:
            settings: Application settings containing API key and model config.
        """
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.model_name
        self._max_tokens = settings.max_tokens
        self._temperature = settings.temperature

    async def generate_response(self, question: str) -> ClaudeResponse:
        """Generate an AI response for the given cloud/IT question.

        Constructs the prompt with the system instruction and user question,
        calls the Claude API, and returns a typed response object.

        Args:
            question: The user's cloud or IT related question.

        Returns:
            A ClaudeResponse containing the answer text and usage metadata.

        Raises:
            ClaudeRateLimitError: If the Anthropic API rate limit is exceeded.
            ClaudeAPIError: If any other API error occurs.
        """
        logger.info("Sending question to Claude (%s): %.80s...", self._model, question)

        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question}],
            )
        except anthropic.RateLimitError as exc:
            logger.warning("Claude API rate limit exceeded: %s", exc)
            raise ClaudeRateLimitError() from exc
        except anthropic.APIStatusError as exc:
            logger.error("Claude API error %d: %s", exc.status_code, exc.message)
            raise ClaudeAPIError(
                message=f"The AI service returned an error: {exc.message}",
                status_code=502,
            ) from exc
        except anthropic.APIConnectionError as exc:
            logger.error("Claude API connection error: %s", exc)
            raise ClaudeAPIError(
                message="Unable to reach the AI service. Please try again.",
                status_code=503,
            ) from exc

        content_block = message.content[0]
        answer = content_block.text if hasattr(content_block, "text") else ""

        logger.info(
            "Claude responded (in=%d, out=%d tokens)",
            message.usage.input_tokens,
            message.usage.output_tokens,
        )

        return ClaudeResponse(
            content=answer,
            model=message.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
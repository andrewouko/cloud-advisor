"""Pydantic schemas for the query endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Incoming user query payload."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question about cloud/IT topics",
        examples=["How do I migrate our on-premise email system to Google Workspace?"],
    )


class QueryResponse(BaseModel):
    """Structured AI response returned to the client."""

    id: str = Field(description="Unique conversation ID (UUID)")
    question: str = Field(description="The original user question")
    answer: str = Field(description="AI-generated response in markdown format")
    timestamp: datetime = Field(description="UTC timestamp of the response")
    model: str = Field(description="The Claude model that generated the response")
    tokens_used: int | None = Field(default=None, description="Total tokens consumed")
    cached: bool = Field(default=False, description="Whether the response was served from cache")
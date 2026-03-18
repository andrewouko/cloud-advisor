"""Pydantic schemas for the history endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    """A single conversation entry stored in history."""

    id: str = Field(description="Unique conversation ID (UUID)")
    question: str = Field(description="The user's original question")
    answer: str = Field(description="The AI-generated response in markdown format")
    timestamp: datetime = Field(description="UTC timestamp of the conversation")


class HistoryResponse(BaseModel):
    """Paginated list of conversation history."""

    conversations: list[HistoryItem] = Field(description="List of conversation entries")
    total: int = Field(description="Total number of conversations in the store")
    limit: int = Field(description="Maximum items returned in this response")
    offset: int = Field(description="Pagination offset used for this response")
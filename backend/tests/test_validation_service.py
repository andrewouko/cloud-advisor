"""Tests for ResponseValidationService."""

import pytest

from app.services.validation_service import ResponseValidationService


@pytest.fixture
def validator() -> ResponseValidationService:
    """Fresh validation service for each test."""
    return ResponseValidationService()


def test_valid_cloud_response(validator: ResponseValidationService) -> None:
    """A well-formed cloud response passes all checks."""
    content = (
        "## Cloud Migration Strategy\n\n"
        "Here are the recommended steps for migrating to Google Cloud:\n\n"
        "1. Assess your current infrastructure\n"
        "2. Choose a migration approach (lift-and-shift vs re-platform)\n"
        "3. Set up your GCP project and networking\n"
    )
    result = validator.validate(content, "How do I migrate to GCP?")
    assert result.is_valid
    assert result.issues == []


def test_empty_response_fails(validator: ResponseValidationService) -> None:
    """Empty response should fail validation."""
    result = validator.validate("", "What is cloud?")
    assert not result.is_valid
    assert any("empty" in issue.lower() for issue in result.issues)


def test_whitespace_only_fails(validator: ResponseValidationService) -> None:
    """Whitespace-only response should fail."""
    result = validator.validate("   \n\t  ", "What is cloud?")
    assert not result.is_valid


def test_too_short_response_fails(validator: ResponseValidationService) -> None:
    """Very short response should fail minimum length check."""
    result = validator.validate("Yes.", "What is cloud?")
    assert not result.is_valid
    assert any("too short" in issue.lower() for issue in result.issues)


def test_refusal_detected(validator: ResponseValidationService) -> None:
    """Response containing refusal patterns should be flagged."""
    content = "I'm sorry, but I cannot help with that request. Please consult a cloud expert."
    result = validator.validate(content, "How do I set up a server?")
    assert not result.is_valid
    assert any("refusal" in issue.lower() for issue in result.issues)


def test_no_domain_relevance_fails(validator: ResponseValidationService) -> None:
    """Response lacking cloud/IT keywords should fail domain check."""
    content = (
        "The recipe for chocolate cake involves mixing flour, sugar, "
        "and cocoa powder together. Bake at 350 degrees for 30 minutes."
    )
    result = validator.validate(content, "Tell me about baking")
    assert not result.is_valid
    assert any("domain" in issue.lower() for issue in result.issues)


def test_unclosed_code_fence_detected(validator: ResponseValidationService) -> None:
    """Unclosed code fence indicates truncation."""
    content = (
        "## Deploy to Cloud\n\n"
        "Run this command:\n\n"
        "```bash\n"
        "gcloud app deploy"
    )
    result = validator.validate(content, "How do I deploy to GCP?")
    assert not result.is_valid
    assert any("truncated" in issue.lower() for issue in result.issues)


def test_closed_code_fence_passes(validator: ResponseValidationService) -> None:
    """Properly closed code fence should pass."""
    content = (
        "## Deploy to Cloud\n\n"
        "Run this command:\n\n"
        "```bash\n"
        "gcloud app deploy\n"
        "```\n\n"
        "This deploys your application to Google Cloud."
    )
    result = validator.validate(content, "How do I deploy to GCP?")
    assert result.is_valid


def test_domain_keywords_in_question_count(validator: ResponseValidationService) -> None:
    """Domain relevance check considers both question and response."""
    content = "Here are the detailed steps you should follow to accomplish this task effectively."
    result = validator.validate(content, "How do I set up a Kubernetes cluster?")
    assert result.is_valid


def test_validate_or_raise_on_valid(validator: ResponseValidationService) -> None:
    """validate_or_raise should not raise for valid responses."""
    content = "## Cloud Security\n\nEnable encryption at rest for all database storage."
    validator.validate_or_raise(content, "How do I secure my database?")


def test_validate_or_raise_on_invalid(validator: ResponseValidationService) -> None:
    """validate_or_raise should raise ValidationError for invalid responses."""
    from app.exceptions import ValidationError

    with pytest.raises(ValidationError):
        validator.validate_or_raise("", "What is cloud?")


def test_summary_for_valid(validator: ResponseValidationService) -> None:
    """Valid result summary should indicate success."""
    content = "## Infrastructure\n\nUse Terraform for infrastructure as code on GCP."
    result = validator.validate(content, "What is IaC?")
    assert "passed" in result.summary.lower()


def test_summary_for_invalid(validator: ResponseValidationService) -> None:
    """Invalid result summary should list issues."""
    result = validator.validate("", "What?")
    assert "failed" in result.summary.lower()
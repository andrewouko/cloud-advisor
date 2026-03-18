"""Response validation service for Claude AI outputs.

Validates Claude responses for structure, quality, domain relevance,
and content safety before returning them to the user. Supports retry
logic when validation fails.
"""

import logging
import re
from dataclasses import dataclass, field

from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Minimum response length (characters) to be considered non-trivial
MIN_RESPONSE_LENGTH = 20

# Maximum retry attempts when validation fails
MAX_VALIDATION_RETRIES = 2

# Patterns indicating a refusal or non-answer
REFUSAL_PATTERNS = [
    r"(?i)i('m| am) (not able|unable) to",
    r"(?i)i can(not|'t) (help|assist|provide|answer)",
    r"(?i)as an ai,?\s+i (don't|do not|cannot|can't)",
    r"(?i)i('m| am) sorry,?\s+(but )?(i )?(can't|cannot|am unable)",
]

# Cloud/IT domain keywords — response should contain at least one
DOMAIN_KEYWORDS = [
    "cloud", "server", "infrastructure", "database", "api", "deploy",
    "migrate", "security", "network", "storage", "kubernetes", "docker",
    "saas", "paas", "iaas", "google", "gcp", "aws", "azure", "workspace",
    "backup", "monitoring", "devops", "ci/cd", "terraform", "ansible",
    "firewall", "encryption", "compliance", "sla", "uptime", "scalab",
    "virtuali", "container", "microservice", "serverless", "endpoint",
    "identity", "authentication", "authoriz", "certificate", "dns",
    "load balanc", "cdn", "data", "analytics", "machine learning",
    "automation", "linux", "windows", "active directory", "sso",
    "multi-cloud", "hybrid", "cost optim", "bandwidth", "latency",
    "availability", "disaster recovery", "failover", "redundan",
    "software", "hardware", "device management", "mdm", "email",
    "collaboration", "productivity", "admin", "config", "provision",
    "integration", "webhook", "rest", "graphql", "sql", "nosql",
    "redis", "postgres", "mongodb", "elasticsearch", "kafka",
    "compute", "instance", "cluster", "node", "pod", "service mesh",
    "observability", "logging", "tracing", "metrics", "dashboard",
    "iam", "rbac", "oauth", "jwt", "vpn", "ssl", "tls", "http",
    "recommend", "solution", "strateg", "implement", "architec",
    "best practice", "step", "approach", "consider", "option",
]

# Patterns suggesting hallucinated URLs
HALLUCINATED_URL_PATTERN = re.compile(
    r"https?://(?!(?:cloud\.google\.com|console\.cloud\.google\.com|"
    r"workspace\.google\.com|admin\.google\.com|support\.google\.com|"
    r"developers\.google\.com|firebase\.google\.com|"
    r"aws\.amazon\.com|docs\.aws\.amazon\.com|"
    r"azure\.microsoft\.com|docs\.microsoft\.com|learn\.microsoft\.com|"
    r"kubernetes\.io|docker\.com|docs\.docker\.com|"
    r"terraform\.io|github\.com|gitlab\.com|"
    r"grafana\.com|prometheus\.io|datadog\.com|"
    r"stackoverflow\.com|en\.wikipedia\.org|"
    r"anthropic\.com|openai\.com|"
    r"example\.com|localhost))[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}"
)


@dataclass
class ValidationResult:
    """Outcome of validating a Claude response."""

    is_valid: bool
    issues: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if self.is_valid:
            return "Response passed all validation checks"
        return f"Validation failed: {'; '.join(self.issues)}"


class ResponseValidationService:
    """Validates Claude responses for quality, relevance, and safety.

    Checks performed:
    1. Non-empty and meets minimum length
    2. Not a refusal or non-answer
    3. Contains domain-relevant content
    4. No hallucinated URLs
    5. Response is not truncated (incomplete markdown)
    """

    def validate(self, response_content: str, question: str) -> ValidationResult:
        """Run all validation checks against a Claude response.

        Args:
            response_content: The raw text response from Claude.
            question: The original user question (for context).

        Returns:
            A ValidationResult indicating pass/fail with details.
        """
        issues: list[str] = []

        # 1. Non-empty / minimum length
        if not response_content or not response_content.strip():
            issues.append("Response is empty")
            return ValidationResult(is_valid=False, issues=issues)

        stripped = response_content.strip()
        if len(stripped) < MIN_RESPONSE_LENGTH:
            issues.append(
                f"Response too short ({len(stripped)} chars, minimum {MIN_RESPONSE_LENGTH})"
            )

        # 2. Refusal detection
        for pattern in REFUSAL_PATTERNS:
            if re.search(pattern, stripped):
                issues.append("Response appears to be a refusal or non-answer")
                break

        # 3. Domain relevance
        lower_content = stripped.lower()
        lower_question = question.lower()
        combined = lower_content + " " + lower_question
        has_domain_keyword = any(kw in combined for kw in DOMAIN_KEYWORDS)
        if not has_domain_keyword:
            issues.append("Response lacks cloud/IT domain relevance")

        # 4. Hallucinated URLs
        suspicious_urls = HALLUCINATED_URL_PATTERN.findall(stripped)
        if suspicious_urls:
            issues.append(
                f"Response contains potentially hallucinated URLs: {suspicious_urls[:3]}"
            )

        # 5. Truncation detection — unclosed markdown fences
        fence_count = stripped.count("```")
        if fence_count % 2 != 0:
            issues.append("Response appears truncated (unclosed code fence)")

        is_valid = len(issues) == 0
        result = ValidationResult(is_valid=is_valid, issues=issues)

        if not is_valid:
            logger.warning(
                "Response validation failed for question '%.60s...': %s",
                question,
                result.summary,
            )
        else:
            logger.debug("Response validation passed for question '%.60s...'", question)

        return result

    def validate_or_raise(self, response_content: str, question: str) -> None:
        """Validate response and raise ValidationError if checks fail.

        Args:
            response_content: The raw text response from Claude.
            question: The original user question.

        Raises:
            ValidationError: If any validation check fails.
        """
        result = self.validate(response_content, question)
        if not result.is_valid:
            raise ValidationError(result.summary)
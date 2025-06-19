"""Model configuration and provider integration for AI Coding CLI."""

import os
import sys
from collections.abc import Callable
from typing import Any, cast

from anthropic.types import (
    CacheControlEphemeralParam,
    DocumentBlockParam,
    ImageBlockParam,
    MessageDeltaUsage,
    MessageParam,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStreamEvent,
    TextBlock,
    TextBlockParam,
    ToolParam,
    ToolResultBlockParam,
    ToolUseBlock,
    ToolUseBlockParam,
    Usage,
)
from anthropic.types import Message as AnthropicMessage
from pydantic import BaseModel
from pydantic_ai import usage
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    ModelResponsePart,
    TextPart,
    ToolCallPart,
)
from pydantic_ai.models import ModelRequestParameters, check_allow_model_requests
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelSettings
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from gsai.config import cli_settings


class AnthropicWithCache(AnthropicModel):
    async def _map_message(  # type: ignore
        self, messages: list[ModelMessage]
    ) -> tuple[list[TextBlockParam], list[MessageParam]]:
        system_prompt, anthropic_messages = await super()._map_message(messages)
        cached_system_prompt = [
            TextBlockParam(
                type="text", text=system_prompt, cache_control={"type": "ephemeral"}
            )
        ]
        for anthropic_message in reversed(anthropic_messages):
            if isinstance(anthropic_message, str):
                continue

            last_message_content = anthropic_message["content"]
            if isinstance(last_message_content, str):
                continue

            *last_message_content_items, last_content_item = last_message_content
            if isinstance(last_content_item, str):
                continue

            else:
                last_content_item = cast(
                    TextBlockParam
                    | ImageBlockParam
                    | ToolUseBlockParam
                    | ToolResultBlockParam
                    | DocumentBlockParam,
                    last_content_item,
                )
                cached_last_content_item = last_content_item
                cached_last_content_item["cache_control"] = CacheControlEphemeralParam(
                    type="ephemeral"
                )
                last_message_content_items.append(cached_last_content_item)
                anthropic_message["content"] = last_message_content_items
                break
        return cached_system_prompt, anthropic_messages

    def _get_tools(
        self, model_request_parameters: ModelRequestParameters
    ) -> list[ToolParam]:
        tools = [
            self._map_tool_definition(r)
            for r in model_request_parameters.function_tools
        ]
        if model_request_parameters.output_tools:
            tools += [
                self._map_tool_definition(r)
                for r in model_request_parameters.output_tools
            ]

        tools[-1]["cache_control"] = CacheControlEphemeralParam(type="ephemeral")
        return tools

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        check_allow_model_requests()
        response = await self._messages_create(
            messages,
            False,
            cast(AnthropicModelSettings, model_settings or {}),
            model_request_parameters,
        )
        model_response = self._process_response(response)
        model_response.usage.requests = 1
        return model_response

    def _process_response(self, response: AnthropicMessage) -> ModelResponse:
        """Process a non-streamed response, and prepare a message to return."""
        items: list[ModelResponsePart] = []
        for item in response.content:
            if isinstance(item, TextBlock):
                items.append(TextPart(content=item.text))
            else:
                assert isinstance(item, ToolUseBlock), "unexpected item type"
                items.append(
                    ToolCallPart(
                        tool_name=item.name,
                        args=cast(dict[str, Any], item.input),
                        tool_call_id=item.id,
                    )
                )

        return ModelResponse(
            items,
            usage=_map_usage(response),
            model_name=response.model,
            vendor_id=response.id,
        )


def _map_usage(message: AnthropicMessage | RawMessageStreamEvent) -> usage.Usage:
    response_usage: Usage | MessageDeltaUsage | None = None
    if isinstance(message, AnthropicMessage):
        response_usage = message.usage
    else:
        if isinstance(message, RawMessageStartEvent):
            response_usage = message.message.usage
        elif isinstance(message, RawMessageDeltaEvent):
            response_usage = message.usage
        else:
            # No usage information provided in:
            # - RawMessageStopEvent
            # - RawContentBlockStartEvent
            # - RawContentBlockDeltaEvent
            # - RawContentBlockStopEvent
            response_usage = None

    if response_usage is None:
        return usage.Usage()

    request_tokens = getattr(response_usage, "input_tokens", None)

    cache_creation_input_tokens = 0
    cache_read_input_tokens = 0
    if isinstance(response_usage, Usage):
        cache_creation_input_tokens = response_usage.cache_creation_input_tokens or 0
        cache_read_input_tokens = response_usage.cache_read_input_tokens or 0

    return usage.Usage(
        # Usage coming from the RawMessageDeltaEvent doesn't have input token data, hence this getattr
        request_tokens=request_tokens,
        response_tokens=response_usage.output_tokens,
        total_tokens=(request_tokens or 0) + response_usage.output_tokens,
        details={
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "cache_read_input_tokens": cache_read_input_tokens,
        },
    )


def _is_test_environment() -> bool:
    """
    Detect if we're running in a test environment.

    Returns:
        True if running in test environment, False otherwise
    """
    # Check for pytest in sys.modules
    if "pytest" in sys.modules:
        return True

    # Check for pytest environment variable
    if os.getenv("PYTEST_CURRENT_TEST"):
        return True

    # Check for CI environment
    if os.getenv("CI"):
        return True

    # Check if API keys are empty (common in test environments)
    if not cli_settings.ANTHROPIC_API_KEY and not cli_settings.OPENAI_API_KEY:
        return True

    return False


def _get_test_api_key(provider: str) -> str:
    """
    Get a dummy API key for test environments.

    Args:
        provider: The provider name ('anthropic' or 'openai')

    Returns:
        A dummy API key for testing
    """
    return f"dummy-{provider}-key-for-tests"


class ValidatedModelName(BaseModel):
    """Validated model name with company and model components."""

    company_name: str
    model_name: str


def create_anthropic_model(model_name: str) -> AnthropicModel:
    """Create Anthropic model with lazy API key access."""
    api_key = cli_settings.ANTHROPIC_API_KEY

    # Use dummy key in test environments if no real key is provided
    if _is_test_environment() and not api_key:
        api_key = _get_test_api_key("anthropic")

    return AnthropicWithCache(
        model_name=model_name,
        provider=AnthropicProvider(api_key=api_key),
    )


def create_openai_model(model_name: str) -> OpenAIModel:
    """Create OpenAI model with lazy API key access."""
    api_key = cli_settings.OPENAI_API_KEY

    # Use dummy key in test environments if no real key is provided
    if _is_test_environment() and not api_key:
        api_key = _get_test_api_key("openai")

    return OpenAIModel(
        model_name=model_name,
        provider=OpenAIProvider(api_key=api_key),
    )


MODEL_NAME_MODEL_MAP: dict[str, Callable[[str], AnthropicModel | OpenAIModel]] = {
    "anthropic": create_anthropic_model,
    "openai": create_openai_model,
}

MODEL_NAME_SETTINGS_MAP: dict[
    str, ModelSettings | AnthropicModelSettings | OpenAIModelSettings
] = {
    "claude-4-sonnet-20250514": ModelSettings(
        temperature=0.1,
        max_tokens=8000,
        parallel_tool_calls=True,
    ),
    "anthropic:claude-3-7-sonnet-latest": ModelSettings(
        temperature=0.1,
        max_tokens=8000,
        parallel_tool_calls=True,
    ),
    "anthropic:claude-3-5-sonnet-latest": ModelSettings(
        temperature=0.1,
        max_tokens=8000,
        parallel_tool_calls=True,
    ),
    "openai:o1": ModelSettings(temperature=0.1, max_tokens=8000),
    "openai:o3-mini": OpenAIModelSettings(
        max_tokens=8000, openai_reasoning_effort="high"
    ),
    "openai:o4-mini": OpenAIModelSettings(
        max_tokens=8000, openai_reasoning_effort="high"
    ),
}


def get_model_name_parts(raw_model_name: str) -> ValidatedModelName:
    """
    Parse and validate model name format.

    Args:
        raw_model_name: Model name in format "provider:model"

    Returns:
        Validated model name components

    Raises:
        ValueError: If model name format is invalid
    """
    model_name_parts = raw_model_name.split(":")

    if len(model_name_parts) != 2:
        raise ValueError(
            "Incorrect Model name, ensure to use prefix like so: anthropic:claude-3-7-sonnet-latest"
        )
    return ValidatedModelName(
        company_name=model_name_parts[0], model_name=model_name_parts[1]
    )


def get_pydantic_ai_model_by_model_name(
    raw_model_name: str,
) -> AnthropicModel | OpenAIModel:
    """
    Get pydantic_ai model instance by model name.

    Args:
        raw_model_name: Model name in format "provider:model"

    Returns:
        Configured model instance

    Raises:
        ValueError: If provider is not supported
    """
    validated_model_name = get_model_name_parts(raw_model_name)
    model_factory = MODEL_NAME_MODEL_MAP.get(validated_model_name.company_name, None)

    if model_factory is None:
        raise ValueError("Could not match company name to a supported model")

    return model_factory(validated_model_name.model_name)


def get_model_settings_by_model_name(raw_model_name: str) -> ModelSettings:
    """
    Get model settings by model name.

    Args:
        raw_model_name: Model name in format "provider:model"

    Returns:
        Model settings configuration
    """
    return MODEL_NAME_SETTINGS_MAP.get(
        raw_model_name, ModelSettings(temperature=0.1, max_tokens=8000)
    )

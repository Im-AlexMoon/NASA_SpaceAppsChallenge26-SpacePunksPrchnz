"""Explicit structured-output adapters; no provider fallback or SDK retries."""

import os


class Provider:
    def __init__(self, settings):
        self.settings = settings

    def generate(self, schema, instructions, payload):
        s = self.settings
        if not s.model:
            raise ValueError("Configure FLAMESAFE_LLM_MODEL explicitly.")
        if s.provider == "gemini":
            from google import genai
            from google.genai import types

            with genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                http_options=types.HttpOptions(
                    timeout=s.timeout_seconds * 1000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            ) as client:
                response = client.models.generate_content(
                    model=s.model,
                    contents=payload,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        response_mime_type="application/json",
                        # Full JSON Schema: `response_schema` rejects the additionalProperties of our strict contracts.
                        response_json_schema=schema.model_json_schema(),
                        max_output_tokens=s.max_output_tokens,
                        temperature=0,
                    ),
                )
                parsed = schema.model_validate_json(response.text or "{}")
                usage = response.usage_metadata
                return parsed, int(usage.total_token_count or 0) if usage else 0
        if s.provider == "openai":
            from openai import OpenAI

            with OpenAI(
                api_key=os.environ["OPENAI_API_KEY"], timeout=s.timeout_seconds, max_retries=0
            ) as client:
                response = client.responses.parse(
                    model=s.model,
                    instructions=instructions,
                    input=payload,
                    text_format=schema,
                    max_output_tokens=s.max_output_tokens,
                    store=False,
                )
                if response.output_parsed is None:
                    raise ValueError("Provider refused or returned incomplete output.")
                return response.output_parsed, int(
                    response.usage.total_tokens
                ) if response.usage else 0
        raise ValueError("Unsupported provider; select gemini or openai.")

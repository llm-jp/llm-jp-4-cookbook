# LLM-jp-4.1 examples for Transformers

Use **Transformers 5.0.0 or later**. [5.0.0](https://github.com/huggingface/transformers/releases/tag/v5.0.0)
is the oldest official release with the `parse_response` API used by these
examples. `uv.lock` pins 5.2.0 for the default environment.

Run the bundled-tokenizer examples with Python 3.13 and the dependencies pinned
in this directory. From the repository root:

```bash
cd llmjp4_transformers
uv sync --locked
uv run --locked example_basic.py
```

The default model is `llm-jp/llm-jp-4.1-8b-thinking`, loaded in `bfloat16` with
`device_map="auto"`. The script prints the prompt, token IDs, decoded response,
reasoning and final content, and token-level Harmony messages. The model's
custom tokenizer and parsers require `trust_remote_code=True`.

## Function calling

From this directory:

```bash
uv run --locked example_function_calling.py
```

The example supplies a `get_weather` tool and asks for the weather in Tokyo and
Osaka. It prints the generated tool calls and Harmony messages; it does not
execute the requested tools or send tool results back to the model. The weather
function is a dummy implementation used to describe the tool schema.

The example supplies a response schema to handle tool recipients in either the
role or channel section.

Edit the model ID in both `from_pretrained` calls, `messages`, `reasoning_effort`,
and generation settings to adapt each example. See the [root README](../README.md)
for model variants, hardware guidance, and the 4.0 compatibility note.

## Validation

Both examples passed with `llm-jp/llm-jp-4.1-8b-thinking`, Transformers 5.0.0
and 5.2.0, Python 3.13.5, and PyTorch 2.10.0 (CUDA 12.8). Checks covered
reasoning/final-content separation and parallel tool-call parsing.
See the [test hardware](../README.md#recorded-test-environment).

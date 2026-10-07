# LLM-jp-4.1 examples for vLLM

Run LLM-jp-4.1 models with vLLM and the
[llm-jp-vllm](https://github.com/llm-jp/llm-jp-vllm) parser library.

## Setup

Use **vLLM 0.30.0 or later** and **llm-jp-vllm 0.1.1 or later**. These are the
oldest official versioned releases that support this cookbook's parser setup.
See the [plugin compatibility requirements](https://github.com/llm-jp/llm-jp-vllm/pull/8).
Both minimum versions are recorded in `pyproject.toml` and pinned in `uv.lock`.

Use Python 3.13 and `uv`. From the repository root:

```bash
cd llmjp4_vllm
uv sync --locked
```

Use a supported GPU and driver with enough memory for the selected model.
Model weights are downloaded on first use unless already cached. The examples
enable `trust_remote_code` to load the model's custom tokenizer.

## Python inference

From this directory:

```bash
uv run --locked example_basic.py
```

The example loads `llm-jp/llm-jp-4.1-8b-thinking` in `bfloat16`, generates a response
to a Japanese prompt, and prints decoded output and Harmony messages. Edit the
model, messages, reasoning effort, or sampling settings in the script to adapt it.

Harmony parsing uses `llm_jp_vllm.llmjp4.harmony.HarmonyMessageParser`. The example
restores the assistant prefix before parsing the generated token IDs. Message
sections are token-ID lists; `start_position` refers to the message's position
in that reconstructed sequence. Output is decoded with the model tokenizer.

## Chat server

From this directory:

```bash
uv run --locked vllm serve llm-jp/llm-jp-4.1-8b-thinking \
    --trust-remote-code \
    --reasoning-parser llmjp4 \
    --reasoning-parser-plugin llm_jp_vllm.llmjp4 \
    --enable-auto-tool-choice \
    --tool-call-parser llmjp4 \
    --tool-parser-plugin llm_jp_vllm.llmjp4 \
    --host 127.0.0.1 \
    --port 8000
```

The module-name plugin options load the installed library and register the
`llmjp4` reasoning and tool parsers. `--enable-auto-tool-choice` allows the model
to request tools supplied by the client.

After the server is ready, run the client in another terminal from this directory:

```bash
bash curl_chat_test.sh
```

The client requires `curl` and sends a streaming request to
`http://localhost:8000/v1/chat/completions`. Both streaming and non-streaming
reasoning extraction are implemented by `llm-jp-vllm`. Set `"stream": false` in
the request for a single response. Keep the model and endpoint in the client
consistent with the server command.

To test function calling, run the following command:

```bash
bash curl_function_calling_test.sh
```

This sends a non-streaming request with `tool_choice: "auto"` and prints the
proposed function name and arguments. It does not execute the function. Add
`"stream": true` to the JSON request to inspect tool-call deltas.

## Validation environment

Validated `llm-jp/llm-jp-4.1-8b-thinking` with vLLM 0.30.0, llm-jp-vllm 0.1.1,
Python 3.13.5, and PyTorch 2.13.0 (CUDA 13.0). The Python example and
streaming/non-streaming API chat and tool calls passed, including reasoning
separation. Parallel tool-call parsing was also checked with the model tokenizer.
See the
[test hardware](../README.md#recorded-test-environment).

For model variants and tokenizer guidance, see the [root README](../README.md).

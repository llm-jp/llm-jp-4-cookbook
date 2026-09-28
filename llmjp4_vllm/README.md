# LLM-jp-4 examples for vLLM

Run LLM-jp-4 models with vLLM and the
[llm-jp-vllm](https://github.com/llm-jp/llm-jp-vllm) parser library.

## Setup

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

The example loads `llm-jp/llm-jp-4-8b-thinking` in `bfloat16`, generates a response
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

The module-name plugin option loads the installed library and registers the
`llmjp4` reasoning parser. The standard vLLM CLI replaces the former
`example_cli.py` wrapper; no parser source files need to be copied locally.

After the server is ready, run the client in another terminal from this directory:

```bash
bash chat_test.sh
```

The client requires `curl` and sends a streaming request to
`http://localhost:8000/v1/chat/completions`. Both streaming and non-streaming
reasoning extraction are implemented by `llm-jp-vllm`. Set `"stream": false` in
the request for a single response. Keep the model and endpoint in the client
consistent with the server command.

To test function calling, run the following command:

```bash
bash fc_test.sh
```

## Validation environment

The pinned dependency set was checked with `llm-jp/llm-jp-4-8b-thinking` on an
NVIDIA RTX 6000 Ada Generation (48 GiB), driver 580.119.02, Python 3.13.5,
PyTorch 2.13.0, and its CUDA 13.0 runtime. The Python example and the standard
CLI server both ran on the GPU; streaming and non-streaming chat requests
returned separate reasoning and final-answer content.

For model variants and tokenizer guidance, see the [root README](../README.md).

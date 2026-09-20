# LLM-jp-4 examples for vLLM

Run LLM-jp-4 models with vLLM and the
[llm-jp-vllm](https://github.com/llm-jp/llm-jp-vllm) parser library.

## Setup

Use Python 3.13 and `uv`. From the repository root:

```bash
cd llmjp4_vllm
uv sync --locked
```

This installs `llm-jp-vllm` and the vLLM build recorded in `uv.lock`. The project
pins `vllm==0.28.1rc1.dev286+g798b557e0` from the official wheel index for commit
`798b557e061b5b7554e2a26ef92f1ec88e9518e9`, which includes
[module-name parser plugin support](https://github.com/vllm-project/vllm/pull/45241).
The inspected vLLM 0.29.0 release does not include that change. The custom index
in `pyproject.toml` is used only for vLLM. The pinned wheels target Linux x86_64
and aarch64.

`llm-jp-vllm` is installed from commit
`daede3e4e196916e8dea9b20d871ba9d4f2d752b` on GitHub, which
[updates the protocol imports for this vLLM API](https://github.com/llm-jp/llm-jp-vllm/commit/daede3e4e196916e8dea9b20d871ba9d4f2d752b).
PyPI version 0.1.0 does not contain that fix. Install Git as well as `uv` to
resolve this source dependency. Other dependencies come from PyPI.

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
uv run --locked vllm serve llm-jp/llm-jp-4-8b-thinking \
    --trust-remote-code \
    --reasoning-parser llmjp4 \
    --reasoning-parser-plugin llm_jp_vllm.llmjp4 \
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

## Validation environment

The pinned dependency set was checked with `llm-jp/llm-jp-4-8b-thinking` on an
NVIDIA RTX 6000 Ada Generation (48 GiB), driver 580.119.02, Python 3.13.5,
PyTorch 2.13.0, and its CUDA 13.0 runtime. The Python example and the standard
CLI server both ran on the GPU; streaming and non-streaming chat requests
returned separate reasoning and final-answer content.

For model variants and tokenizer guidance, see the [root README](../README.md).

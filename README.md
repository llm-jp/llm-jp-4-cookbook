# LLM-jp-4 Series Cookbook

Examples for running LLM-jp-4.0/4.1 models with Hugging Face Transformers, vLLM, and
llama.cpp, including chat templates, reasoning output, and Harmony message parsing.

Author: Yusuke Oda (@odashi)

## Choose a runtime

| Runtime | Use case | Entry point |
| --- | --- | --- |
| Transformers | Run inference in Python and inspect generated tokens and parsed messages. | [Basic example](llmjp4_transformers/example_basic.py) |
| vLLM | Run inference in Python or serve a chat API with llm-jp-vllm. | [Basic example](llmjp4_vllm/example_basic.py), [setup and server guide](llmjp4_vllm/README.md) |
| llama.cpp | Run GGUF models with a command-line chat client or local server. | [Installation and usage guide](llmjp4_llama-cpp/README.md) |

The Python examples use `llm-jp/llm-jp-4.1-8b-thinking` by default. Each Python
runtime has its own dependency manifest and lockfile; there is no root Python
project. Install and run commands from the runtime directory you choose.

### Minimum runtime releases

Use the following minimum official stable releases **or later**.
`uv.lock` records the exact Python dependency versions used for reproducible runs.

| Runtime | Minimum official stable release | Required support |
| --- | --- | --- |
| Transformers | [5.0.0](https://github.com/huggingface/transformers/releases/tag/v5.0.0) | `parse_response` for the bundled response schemas. |
| vLLM | [0.30.0](https://github.com/vllm-project/vllm/releases/tag/v0.30.0) | Module-name parser plugins; also use [llm-jp-vllm 0.1.1](https://github.com/llm-jp/llm-jp-vllm/tree/v0.1.1) or later. |
| llama.cpp | [v0.6.0](https://github.com/ggml-org/llama.cpp/releases/tag/v0.6.0) | Native LLM-jp-4.1 Harmony chat parsing for GGUF models. |

## Using LLM-jp-4.0 models

LLM-jp-4.1 is backward-compatible with the 4.0 series and is the default in this
cookbook. To use a 4.0 model with the Python examples or vLLM server, replace
`llm-jp/llm-jp-4.1-8b-thinking` with `llm-jp/llm-jp-4-8b-thinking` in the model
loading calls, server command, and client requests. The 4.0 repository names use
`llm-jp-4-`, not `llm-jp-4.0-`. Keep the bundled tokenizer and parser settings.
Tool-calling improvements are part of 4.1; the function-calling examples target
4.1 models.

The llama.cpp instructions target 4.1 GGUF files. Original 4.0 GGUF chat
templates lack the declaration needed to select the LLM-jp-4.1 Harmony parser.

## Run the Python examples

### Requirements

- Python 3.13 or later. Both projects select Python 3.13 in `.python-version`.
- `uv` for installing the dependencies recorded in each `uv.lock`.
- Hardware and drivers suitable for the selected runtime and model. The examples
  load the 8B model in `bfloat16`; see the recorded test environment below.
- Network access to download dependencies and model files on the first run, or
  copies already available locally.

The examples enable `trust_remote_code=True` to load the custom tokenizer and
model-bundled helpers. vLLM parsing is provided separately by `llm-jp-vllm`.
The remote-code option allows Python code from the
model repository to run, so use model repositories you trust. The llama.cpp
workflow uses GGUF files and does not use this Python option.

### Transformers

From the repository root:

```bash
cd llmjp4_transformers
uv sync --locked
uv run --locked example_basic.py
```

The script prints the chat prompt, input and generated token IDs, decoded output,
the result of `tokenizer.parse_response`, and token-level Harmony messages. It
uses `device_map="auto"` to place the model.

To change the model, update both `from_pretrained` calls in
[`example_basic.py`](llmjp4_transformers/example_basic.py). Edit `messages` to
change the prompt, `reasoning_effort` to choose the thinking effort, and
`model.generate` arguments to change the generation settings. These are source
settings, not command-line options.

For tool-call generation and parsing, run `uv run --locked example_function_calling.py`.
See the [Transformers guide](llmjp4_transformers/README.md) for details.

### vLLM: Python inference

The vLLM environment includes [llm-jp-vllm](https://github.com/llm-jp/llm-jp-vllm)
for Harmony and reasoning parsing. It requires vLLM 0.30.0 or later and
`llm-jp-vllm` 0.1.1 or later; see the [vLLM setup guide](llmjp4_vllm/README.md)
for setup details.

From the repository root:

```bash
cd llmjp4_vllm
uv sync --locked
uv run --locked example_basic.py
```

The script prints the prompt, generated token IDs, decoded output, and parsed
Harmony messages. Change the model in `LLM(...)`, the prompt in `messages`, and
generation settings in `SamplingParams(...)` in
[`example_basic.py`](llmjp4_vllm/example_basic.py).

The example deliberately decodes `output.token_ids` with the model tokenizer.
Its source documents whitespace problems with `output.text`; preserve this
decoding path when adapting the example.

### vLLM: chat server

After installing the vLLM project's dependencies, run this command from
`llmjp4_vllm`:

```bash
uv run --locked vllm serve llm-jp/llm-jp-4.1-8b-thinking \
    --reasoning-parser llmjp4 \
    --reasoning-parser-plugin llm_jp_vllm.llmjp4 \
    --enable-auto-tool-choice \
    --tool-call-parser llmjp4 \
    --tool-parser-plugin llm_jp_vllm.llmjp4 \
    --trust-remote-code \
    --host 127.0.0.1 \
    --port 8000
```

The plugin options import `llm-jp-vllm` and register the `llmjp4` reasoning and
tool parsers with the standard vLLM CLI. Once the server is ready, open another
terminal at the repository root and send the supplied streaming request:

```bash
cd llmjp4_vllm
bash curl_chat_test.sh
```

This requires `curl` and calls `http://localhost:8000/v1/chat/completions`.
If you change the served model or port, also update
[`curl_chat_test.sh`](llmjp4_vllm/curl_chat_test.sh) and
[`curl_function_calling_test.sh`](llmjp4_vllm/curl_function_calling_test.sh).

`llm-jp-vllm` separates reasoning and final-answer content in both streaming and
non-streaming responses. The supplied request uses `"stream": true`; change it
to `false` to receive a single response.

Run `bash curl_function_calling_test.sh` from `llmjp4_vllm` to request a tool call.
The client displays the proposed function name and arguments; it does not execute
the function.

## Run GGUF models with llama.cpp

Follow the [llama.cpp guide](llmjp4_llama-cpp/README.md) for installation
instructions and `llama cli` / `llama serve` examples.

Use upstream `ggml-org/llama.cpp` **v0.6.0 or later**. The `-hf` option in the
examples downloads the selected GGUF model from Hugging Face and caches it.
Model files are not included in this repository.

## Model variants and message handling

The [LLM-jp-4.1 release](https://llm-jp.nii.ac.jp/blog/llm-jp-4-1/) provides
`8b-thinking`, `32b-a3b-thinking` (MoE), and `33b-thinking` models, with GGUF
variants. The examples default to `8b-thinking` and support reasoning effort
`low`, `medium`, or `high`. Base models from the 4.0 series require adaptation
of these chat examples.

The chat models use Harmony messages to represent roles, channels, content, and
message endings. The examples pass `reasoning_effort="medium"` to the model's
chat template for the thinking model.

When adapting the examples:

- **Load the bundled tokenizer.** LLM-jp-4.1 uses a custom Unigram byte-fallback
  tokenizer with a vocabulary converted from llm-jp-tokenizer v4.0. The Python
  examples use `trust_remote_code=True` to load it. Do not substitute the
  `openai-harmony` tokenizer; its token IDs differ.
- **Apply the model's chat template.** Use `apply_chat_template` with
  `add_generation_prompt=True` for chat input. Input containing literal strings
  that resemble special tokens, such as `<|...|>`, may require custom encoding.
- **Parse token IDs when message boundaries matter.** Decoded text alone can be
  ambiguous when content resembles special tokens. Transformers exposes
  `tokenizer.parse_harmony_message`; the vLLM example imports
  `HarmonyMessageParser` from `llm_jp_vllm.llmjp4.harmony`.
- **Account for the assistant prefix.** Both Python examples prepend
  `<|start|>assistant` before parsing generated IDs because that prefix is already
  part of the input prompt. Preserve this context when reconstructing messages.

Base models do not have the chat behavior of the fine-tuned variants. They also
bundle tokenizer helpers; handling special tokens or extending the vocabulary
can require the same care. The supplied chat examples should be adapted before
using a base model.

## Recorded test environment

The repository records the following hardware environment for its examples.
This is a reference environment, not a statement of minimum requirements.
For the runtime versions and model sizes tested, see
the [Transformers validation](llmjp4_transformers/README.md#validation),
[vLLM validation](llmjp4_vllm/README.md#validation-environment), and
[llama.cpp validation](llmjp4_llama-cpp/README.md#validation) notes.

| Component | Configuration |
| --- | --- |
| CPU | Intel Core i9-14900K |
| RAM | 32 GiB |
| GPU | NVIDIA RTX 6000 Ada Generation |
| OS | Debian GNU/Linux 12 |
| NVIDIA driver | 580.119.02 |
| CUDA library | 12.8 (Transformers and llama.cpp); 13.0 (vLLM) |

## Development and license

See [AGENTS.md](AGENTS.md) for repository structure, development guidance, and
validation commands.

This repository is licensed under [Apache License 2.0](LICENSE).

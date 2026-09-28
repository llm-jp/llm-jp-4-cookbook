# LLM-jp-4 Cookbook

Examples for running LLM-jp-4 models with Hugging Face Transformers, vLLM, and
llama.cpp, including chat templates, reasoning output, and Harmony message parsing.

Author: Yusuke Oda (@odashi)

## Choose a runtime

| Runtime | Use case | Entry point |
| --- | --- | --- |
| Transformers | Run inference in Python and inspect generated tokens and parsed messages. | [Basic example](llmjp4_transformers/example_basic.py) |
| vLLM | Run inference in Python or serve a chat API with llm-jp-vllm. | [Basic example](llmjp4_vllm/example_basic.py), [setup and server guide](llmjp4_vllm/README.md) |
| llama.cpp | Run GGUF models with a command-line chat client or local server. | [Build and usage guide](llmjp4_llama-cpp/README.md) |

The Python examples use `llm-jp/llm-jp-4-8b-thinking` by default. Each Python
runtime has its own dependency manifest and lockfile; there is no root Python
project. Install and run commands from the runtime directory you choose.

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
uv run --locked vllm serve llm-jp/llm-jp-4-8b-thinking \
    --reasoning-parser llmjp4 \
    --reasoning-parser-plugin llm_jp_vllm.llmjp4 \
    --trust-remote-code \
    --host 127.0.0.1 \
    --port 8000
```

The plugin option imports `llm-jp-vllm` and registers the `llmjp4` parser with
the standard vLLM CLI. Once the server is ready, open another terminal at the
repository root and send the supplied streaming request:

```bash
cd llmjp4_vllm
bash chat_test.sh
```

This requires `curl` and calls `http://localhost:8000/v1/chat/completions`.
If you change the served model or port, also update
[`chat_test.sh`](llmjp4_vllm/chat_test.sh).

`llm-jp-vllm` separates reasoning and final-answer content in both streaming and
non-streaming responses. The supplied request uses `"stream": true`; change it
to `false` to receive a single response.

## Run GGUF models with llama.cpp

Follow the [llama.cpp guide](llmjp4_llama-cpp/README.md) for build commands,
optional CUDA support, `llama-cli`, and `llama-server` examples.

That guide uses the LLM-jp fork of llama.cpp to address tokenizer and chat-parsing
issues with LLM-jp-4 GGUF models. Use the documented fork and keep `--jinja`
enabled for the model's embedded chat template. Supply your own GGUF model path;
model files are not included in this repository.

## Model variants and message handling

| Model suffix | Intended behavior |
| --- | --- |
| `-instruct` | Chat responses without reasoning. |
| `-thinking` | Chat responses with reasoning effort set to `low`, `medium`, or `high`. |
| `-base` | Base language modeling without chat fine-tuning. |

The chat models use Harmony messages to represent roles, channels, content, and
message endings. The examples pass `reasoning_effort="medium"` to the model's
chat template for the thinking model.

When adapting the examples:

- **Load the bundled tokenizer.** LLM-jp-4 provides custom SentencePiece tokenizer
  handling. The Python examples use `trust_remote_code=True` to load it.
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

The repository records the following environment for its examples. This is a
reference environment, not a statement of minimum hardware requirements.
The updated vLLM setup was also validated with its CUDA 13.0 runtime; see the
[vLLM validation environment](llmjp4_vllm/README.md#validation-environment).

| Component | Configuration |
| --- | --- |
| CPU | Intel Core i9-14900K |
| RAM | 32 GiB |
| GPU | NVIDIA RTX 6000 Ada Generation |
| OS | Debian GNU/Linux 12 |
| NVIDIA driver | 580.119.02 |
| CUDA library | 12.8 |

## Development and license

See [AGENTS.md](AGENTS.md) for repository structure, development guidance, and
validation commands.

This repository is licensed under [Apache License 2.0](LICENSE).

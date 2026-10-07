# LLM-jp-4.1 examples for llama.cpp

Run LLM-jp-4.1 GGUF models with upstream
[ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).

Use **v0.6.0 or later**. [v0.6.0](https://github.com/ggml-org/llama.cpp/releases/tag/v0.6.0)
is the oldest official stable release that includes the
[LLM-jp-4.1 Harmony parser](https://github.com/ggml-org/llama.cpp/pull/29681).
For original 4.0 GGUF files, see the
[compatibility note](../README.md#using-llm-jp-40-models).

## Requirements

Install CMake and a C++ compiler, then build the minimum supported stable
release (or choose a newer stable release tag):

```bash
git clone https://github.com/ggml-org/llama.cpp --branch v0.6.0 --depth 1
cd llama.cpp
cmake -B build -DLLAMA_BUILD_IS_DEV=OFF
cmake --build build --config Release -j --target llama-cli llama-server
```

`LLAMA_BUILD_IS_DEV=OFF` builds the release tag without the default `-dev`
version suffix. Check the result with `./build/bin/llama-cli --version`.

When using NVIDIA GPUs, install the CUDA toolkit and build with CUDA support.
Run these commands from the cloned `llama.cpp` directory:

```bash
cmake -B build -DLLAMA_BUILD_IS_DEV=OFF -DGGML_CUDA=ON
cmake --build build --config Release -j --target llama-cli llama-server
```

Download a GGUF file from the
[official 8B GGUF repository](https://huggingface.co/llm-jp/llm-jp-4.1-8b-thinking-gguf/tree/main),
such as `llm-jp-4.1-8b-thinking-Q4_K_M.gguf`, and replace the paths below.
Run the following commands from the cloned `llama.cpp` directory. Keep `--jinja`
enabled to use the embedded chat template.

## Chat with `llama-cli`

`llama-cli` provides a command-line interface to chat with LLM-jp-4.1 GGUF models.

```bash
./build/bin/llama-cli \
    --model /path/to/llm-jp-4.1-8b-thinking-Q4_K_M.gguf \
    --jinja
```

## OpenAI-compatible local server

`llama-server` launches an OpenAI-compatible server.

```bash
./build/bin/llama-server \
    --model /path/to/llm-jp-4.1-8b-thinking-Q4_K_M.gguf \
    --alias llm-jp-4.1-8b-thinking \
    --jinja \
    --host 127.0.0.1 \
    --port 8080
```

After starting the server, send chat completion requests to `http://127.0.0.1:8080/v1/chat/completions`.

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llm-jp-4.1-8b-thinking",
        "messages": [
            {"role": "user", "content": "Transformer 言語モデルについて教えてください。"}
        ],
        "max_tokens": 512
    }'
```

The response separates reasoning from final-answer content. Add `"stream": true`
to receive streaming deltas. The same server accepts OpenAI-compatible `tools`
and `tool_choice` fields for function calling.

## Validation

Validated v0.6.0 with GCC 12.2.0 and CUDA 12.8 using
`llm-jp-4.1-33b-thinking-Q4_K_M.gguf`. The upstream `test-chat` suite, CLI chat,
and streaming/non-streaming API chat and tool calls passed. The server used a
4096-token context and one slot. The 8B GGUF example was not tested.
See the [test hardware](../README.md#recorded-test-environment).

# LLM-jp-4 examples for llama.cpp

This directory provides examples to run LLM-jp-4 GGUF models with [the LLM-jp fork of llama.cpp](https://github.com/llm-jp/llama.cpp).

> [!IMPORTANT]
> LLM-jp-4 GGUF models require this fork to work around tokenizer handling issues.
> If users use the upstream `ggml-org/llama.cpp` build as-is, chat parsing fails for `-thinking` models.
> We're in the process of upstreaming the necessary fixes, but in the meantime, please use the LLM-jp fork to run LLM-jp-4 GGUF models.

## Requirements

Build and install the LLM-jp fork of `llama.cpp`:

```bash
git clone https://github.com/llm-jp/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release -j
```

When using NVIDIA GPUs, build `llama.cpp` with CUDA support:

```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j
```

## Chat with `llama-cli`

`llama-cli` provides a command-line interface to chat with LLM-jp-4 GGUF models.

```bash
./build/bin/llama-cli \
    --model /path/to/llm-jp-4-8b-thinking-Q4_K_M.gguf \
    --jinja
```

## OpenAI-compatible local server

`llama-server` launches an OpenAI-compatible server.

```bash
./build/bin/llama-server \
    --model /path/to/llm-jp-4-8b-thinking-Q4_K_M.gguf \
    --jinja \
    --host 127.0.0.1 \
    --port 8080
```

After starting the server, send chat completion requests to `http://127.0.0.1:8080/v1/chat/completions`.

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llm-jp-4-8b-thinking-Q4_K_M",
        "messages": [
            {"role": "user", "content": "Transformer 言語モデルについて教えてください。"}
        ],
        "max_tokens": 512
    }'
```

## Notes

* Use the LLM-jp fork of `llama.cpp`. The upstream `ggml-org/llama.cpp` build fails chat parsing because of tokenizer handling issues.
* Keep `--jinja` enabled when using the chat template embedded in the GGUF file.

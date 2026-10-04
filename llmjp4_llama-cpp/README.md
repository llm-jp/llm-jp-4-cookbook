# LLM-jp-4.1 examples for llama.cpp

This directory provides examples to run LLM-jp-4.1 GGUF models with llama.cpp.

> [!IMPORTANT]
> LLM-jp-4.1 GGUF models can be served with the upstream [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) build as-is.

## Requirements

Build and install [the LLM-jp fork of `llama.cpp`](https://github.com/llm-jp/llama.cpp) for the CLI example:

```bash
git clone https://github.com/llm-jp/llama.cpp -b llm-jp-4.1 --single-branch # for LLM-jp-4 series, specify `-b llm-jp-4` instead
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

`llama-cli` provides a command-line interface to chat with LLM-jp-4.1 GGUF models.

```bash
./build/bin/llama-cli \
    --model /path/to/llm-jp-4.1-8b-thinking-Q4_K_M.gguf \
    --jinja
```

## OpenAI-compatible local server

`llama-server` launches an OpenAI-compatible server.

For the stock upstream server, start outside the fork checkout and build llama.cpp:

```bash
git clone https://github.com/ggml-org/llama.cpp.git llama.cpp-stock
cd llama.cpp-stock
cmake -B build
cmake --build build --config Release -j
```

For NVIDIA GPUs, add `-DGGML_CUDA=ON` to the configure command. Run the server from this checkout:

```bash
./build/bin/llama-server \
    --model /path/to/llm-jp-4.1-8b-thinking-Q4_K_M.gguf \
    --jinja \
    --host 127.0.0.1 \
    --port 8080
```

After starting the server, send chat completion requests to `http://127.0.0.1:8080/v1/chat/completions`.

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llm-jp-4.1-8b-thinking-Q4_K_M",
        "messages": [
            {"role": "user", "content": "Transformer 言語モデルについて教えてください。"}
        ],
        "max_tokens": 512
    }'
```

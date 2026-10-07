# LLM-jp-4.1 examples for llama.cpp

This directory provides examples to run LLM-jp-4.1 GGUF models with [llama.cpp](https://github.com/ggml-org/llama.cpp).

## Requirements

Install [llama.cpp](https://github.com/ggml-org/llama.cpp) by following the official installation instructions.

> [!IMPORTANT]
> LLM-jp-4.1 is supported in llama.cpp v0.6.0 or later.

## Chat from the command line

Use `llama cli` to chat with an LLM-jp-4.1 GGUF model from the command line.

```bash
llama cli -hf llm-jp/llm-jp-4.1-8b-thinking-gguf:Q4_K_M
```

## OpenAI-compatible local server

Use llama server to launch a local server with an OpenAI-compatible API.

```bash
llama server -hf llm-jp/llm-jp-4.1-8b-thinking-gguf:Q4_K_M --host 127.0.0.1 --port 8080
```

After starting the server, send chat completion requests to `http://127.0.0.1:8080/v1/chat/completions`.

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llm-jp-4.1-8b-thinking-Q4_K_M",
        "messages": [
            {"role": "user", "content": "Tell me about Transformer-based language models"}
        ],
        "max_tokens": 512
    }'
```

# LLM-jp-4.1 examples for llama.cpp

Run LLM-jp-4.1 GGUF models with upstream
[ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).

Use **v0.6.0 or later**. [v0.6.0](https://github.com/ggml-org/llama.cpp/releases/tag/v0.6.0)
is the oldest official stable release that includes the
[LLM-jp-4.1 Harmony parser](https://github.com/ggml-org/llama.cpp/pull/29681).
For original 4.0 GGUF files, see the
[compatibility note](../README.md#using-llm-jp-40-models).

## Requirements

Install llama.cpp by following the
[official installation instructions](https://github.com/ggml-org/llama.cpp#quick-start).

## Chat from the command line

Use `llama cli` to chat with an LLM-jp-4.1 GGUF model from the command line.
The `-hf` option downloads the selected GGUF model from Hugging Face and caches it.

```bash
llama cli -hf llm-jp/llm-jp-4.1-8b-thinking-gguf:Q4_K_M
```

## OpenAI-compatible local server

Use `llama serve` to launch a local server with an OpenAI-compatible API.

```bash
llama serve -hf llm-jp/llm-jp-4.1-8b-thinking-gguf:Q4_K_M \
    --alias llm-jp-4.1-8b-thinking \
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
            {"role": "user", "content": "Tell me about Transformer-based language models"}
        ],
        "max_tokens": 512
    }'
```

The response separates reasoning from final-answer content. Add `"stream": true`
to receive streaming deltas. The same server accepts OpenAI-compatible `tools`
and `tool_choice` fields for function calling.

## Validation

Validated a source build of v0.6.0 with GCC 12.2.0 and CUDA 12.8 using
`llm-jp-4.1-33b-thinking-Q4_K_M.gguf`. The upstream `test-chat` suite, CLI chat,
and streaming/non-streaming API chat and tool calls passed. The server used a
4096-token context and one slot. The 8B GGUF example was not tested.
See the [test hardware](../README.md#recorded-test-environment).

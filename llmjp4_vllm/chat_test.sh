#!/bin/bash

# Example script to communicate with the vLLM server using curl.
# Before running this script, make sure to start the vLLM server with LLM-jp-4 models loaded.
# See README.md for the vllm serve command with the llm-jp-vllm plugin.

# "stream": true requests streaming mode, which periodically returns partial responses.
# This mode returns both the reasoning and the final response.

# "stream": false requests a single response. llm-jp-vllm also supports
# extracting reasoning and the final response in non-streaming mode.

curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llm-jp/llm-jp-4-8b-thinking",
    "messages": [{"role": "user", "content": "二次方程式の解の公式を導出して下さい。"}],
    "stream": true
  }'

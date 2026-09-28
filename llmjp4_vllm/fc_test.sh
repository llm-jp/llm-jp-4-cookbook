#!/bin/bash

# Example script to communicate with the vLLM server using curl.
# Before running this script, make sure to start the vLLM server with LLM-jp-4.1 models loaded.
# See README.md for the vllm serve command with the llm-jp-vllm plugin.

# "stream": true requests streaming mode, which periodically returns partial responses.
# This mode returns both the reasoning and the final response.

# "stream": false requests a single response. llm-jp-vllm also supports
# extracting reasoning and the final response in non-streaming mode.

curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llm-jp/llm-jp-4.1-8b-thinking",
    "messages": [
      {
        "role": "user",
        "content": "東京の現在時刻を調べてください。"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_time",
          "description": "指定された場所の現在時刻を取得する",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "場所"
              }
            },
            "required": ["location"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'

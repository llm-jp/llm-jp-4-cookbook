#!/bin/bash

# Example script to test function calling with the vLLM server.
# Before running this script, make sure to start the vLLM server with an LLM-jp-4.1 model loaded.
# See README.md for the vllm serve command with the llm-jp-vllm plugin.

# This request provides a get_current_time function that takes a location as an argument.
# With "tool_choice": "auto", the model decides whether to call the function based on the user's request.
# The response includes the function name and arguments when the model chooses to make a tool call.

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

# This file contains code to use LLM-jp-4.1 models with Hugging Face Transformers library.

import torch

from transformers import AutoModelForCausalLM, AutoTokenizer


# NOTE (kiyomaru): This change should be upstreamed to llm-jp-tokenizer.
# The model's bundled schema does not recognize Harmony tool calls whose
# recipient appears in the role section, so provide a compatible schema.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "role": {"const": "assistant"},
        "content": {
            "type": "string",
            "x-regex": (
                r"<\|channel\|>final<\|message\|>(.*?)"
                r"(?:<\|end\|>|<\|return\|>|$)"
            ),
        },
        "thinking": {
            "type": "string",
            "x-regex": (
                r"<\|channel\|>analysis<\|message\|>(.*?)<\|end\|>"
            ),
        },
        "tool_calls": {
            "x-regex-iterator": (
                r"((?:to=functions\..*?<\|channel\|>commentary|"
                r"<\|channel\|>commentary.*?to=functions\.[^\s<]+)"
                r".*?<\|message\|>.*?)(?:<\|end\|>|<\|call\|>|$)"
            ),
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"const": "function"},
                    "function": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "x-regex": r"to=functions\.([^\s<]+)",
                            },
                            "arguments": {
                                "type": "object",
                                "x-regex": r"<\|message\|>(.*)",
                                "x-parser": "json",
                                "additionalProperties": {},
                            },
                        },
                    },
                },
            },
        },
    },
}


def get_weather(city: str) -> str:
    """
    Get the current weather for a city.

    Args:
        city: The city to get the weather for.
    """
    # Dummy implementation for demonstration.
    return f"The weather in {city} is sunny, with a temperature of 25°C."


def main():
    tokenizer = AutoTokenizer.from_pretrained(
        "llm-jp/llm-jp-4.1-8b-thinking",
        # trust_remote_code is required to load custom tokenizer and reasoning parser.
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        "llm-jp/llm-jp-4.1-8b-thinking",
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    messages = [
        {"role": "user", "content": "東京と大阪の天気を教えてください。"},
    ]

    tools = [get_weather]

    prompt: str = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
        reasoning_effort="medium",
    )

    print("--- Prompt ---")
    print(prompt)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    print("--- Input IDs ---")
    print(inputs["input_ids"][0].tolist())

    with torch.no_grad():
        output_tensor = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

    generated_ids: list[int] = output_tensor[
        0, inputs["input_ids"].shape[1]:
    ].tolist()

    print("--- Generated IDs ---")
    print(generated_ids)

    response = tokenizer.decode(generated_ids)

    print("\n--- Response ---")
    print(response)

    parsed = tokenizer.parse_response(response, schema=RESPONSE_SCHEMA)

    print("\n--- Parsed Response ---")
    print("Role:", parsed.get("role"))
    print("Thinking:", parsed.get("thinking"))
    print("Content:", parsed.get("content"))
    print("Tool Calls:", parsed.get("tool_calls"))

    # Harmony parser is bundled as the parse_harmony_message method of the tokenizer.
    # This function accepts a list of token IDs (not strings)
    # and returns a list of Harmony's message objects with split tokens.

    # To correctly parse the response,
    # we need to include the prefill tokens for the assistant's response.
    response_prefill = tokenizer.encode("<|start|>assistant", add_special_tokens=False)
    parsed_harmony = tokenizer.parse_harmony_message(
        response_prefill + generated_ids
    )

    print("\n--- Parsed Harmony Messages ---")
    for i, message in enumerate(parsed_harmony, start=1):
        print(f"Message {i}:")
        print("  End Type:", message.end)

        if message.role:
            print("  Role Tokens:", message.role.token_ids)
            print("  Role Text:", repr(tokenizer.decode(message.role.token_ids)))
            print("  Role Start Position:", message.role.start)
        if message.channel:
            print("  Channel Tokens:", message.channel.token_ids)
            print("  Channel Text:", repr(tokenizer.decode(message.channel.token_ids)))
            print("  Channel Start Position:", message.channel.start)
        if message.constrain:
            print("  Constrain Tokens:", message.constrain.token_ids)
            print("  Constrain Text:", repr(tokenizer.decode(message.constrain.token_ids)))
            print("  Constrain Start Position:", message.constrain.start)
        if message.content:
            print("  Content Tokens:", message.content.token_ids)
            print("  Content Text:", repr(tokenizer.decode(message.content.token_ids)))
            print("  Content Start Position:", message.content.start)


if __name__ == "__main__":
    main()

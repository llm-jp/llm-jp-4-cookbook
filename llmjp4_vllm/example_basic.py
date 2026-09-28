# Example script to use LLM-jp-4 models with vLLM.

from vllm import LLM, SamplingParams

from llm_jp_vllm.llmjp4.harmony import HarmonyMessageParser


def main():
    llm = LLM(
        model="llm-jp/llm-jp-4.1-8b-thinking",
        dtype="bfloat16",
        # trust_remote_code is required to load the model's custom tokenizer.
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()

    messages = [
        {"role": "user", "content": "日本語で自己紹介してください。"},
    ]

    prompt: str = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        reasoning_effort="medium",
    )

    print("--- Prompt ---")
    print(prompt)

    sampling_params = SamplingParams(
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
    )

    outputs = llm.generate([prompt], sampling_params)
    output = outputs[0].outputs[0]

    print("--- Generated IDs ---")
    print(output.token_ids)

    # NOTE(odashi):
    # Don't use `output.text` at this moment.
    # It doesn't handle whitespaces appropriately.
    decoded_output = tokenizer.decode(output.token_ids)
    print("\n--- Decoded Output ---")
    print(decoded_output)

    parser = HarmonyMessageParser(tokenizer)
    # Generation continues after this assistant prefix in the input prompt.
    response_prefill = tokenizer.encode("<|start|>assistant", add_special_tokens=False)
    print("\n--- Parsed Harmony Messages ---")
    for i, message in enumerate(
        parser.iter_messages(response_prefill + list(output.token_ids)), start=1
    ):
        print(f"Message {i}:")

        # The end type can be "END", "CALL", or "INCOMPLETE".
        print("  End Type:", message.end)
        print("  Message Start Position:", message.start_position)

        if message.role:
            print("  Role Tokens:", message.role)
            print("  Role Text:", repr(tokenizer.decode(message.role)))
        if message.channel:
            print("  Channel Tokens:", message.channel)
            print("  Channel Text:", repr(tokenizer.decode(message.channel)))
        if message.constrain:
            print("  Constrain Tokens:", message.constrain)
            print("  Constrain Text:", repr(tokenizer.decode(message.constrain)))
        if message.content:
            print("  Content Tokens:", message.content)
            print("  Content Text:", repr(tokenizer.decode(message.content)))


if __name__ == "__main__":
    main()

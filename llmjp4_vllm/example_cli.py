# This script works similarly to the `vllm` CLI command,
# but registers additional components.
#
# Usage: python example_cli.py [...rest of vllm CLI arguments]
#
# Example:
# The following command runs the llm-jp-4-8b-thinking model with the llmjp4 reasoning parser.
# python example_cli.py serve llm-jp/llm-jp-4-8b-thinking --reasoning-parser llmjp4 --trust-remote-code

from vllm.entrypoints.cli import main as cli_main

# Load the custom reasoning before launching the CLI.
import llmjp4_reasoning_parser


if __name__ == "__main__":
    cli_main.main()


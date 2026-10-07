# Developer and Agent Guide

## Purpose and scope

This repository is a cookbook for running LLM-jp-4.1 models with Transformers,
vLLM, and llama.cpp. Keep examples small, readable, and runnable on their own.
The root [README.md](README.md) is the user-facing entry point; this file covers
maintenance and agent workflows.

Communicate with the user in Japanese. Write repository documentation in English.
Japanese prompts in examples are intentional and do not need translation.

## Repository map

| Path | Responsibility |
| --- | --- |
| `llmjp4_transformers/example_basic.py` | Model loading, chat templating, generation, and parsing with the model's bundled tokenizer helpers. |
| `llmjp4_transformers/example_function_calling.py` | Tool-call generation and parsing with the model's bundled tokenizer. |
| `llmjp4_transformers/{pyproject.toml,uv.lock,.python-version}` | Independent Transformers environment. |
| `llmjp4_vllm/example_basic.py` | Offline generation, explicit token decoding, and Harmony parsing through llm-jp-vllm. |
| `llmjp4_vllm/README.md` | Dependency setup and standard vLLM CLI commands with module-name plugin loading. |
| `llmjp4_vllm/curl_chat_test.sh` | Manual streaming chat request to a running server. |
| `llmjp4_vllm/curl_function_calling_test.sh` | Manual tool-call request to a running server. |
| `llmjp4_vllm/{pyproject.toml,uv.lock,.python-version}` | Independent vLLM environment. |
| `llmjp4_llama-cpp/README.md` | Instructions for building and using upstream llama.cpp v0.6.0 or later. |

There is no root Python package, shared uv workspace, automated test suite, or CI
configuration in the tracked repository. The llama.cpp directory contains
documentation, not a vendored runtime. Model weights are not tracked; `models/`
and `.venv` directories are ignored.

## Environment and dependencies

Both Python projects require Python 3.13 or later and select 3.13 through
`.python-version`. Run `uv` inside the relevant runtime directory.

```bash
# From the repository root; choose the runtime you are working on.
cd llmjp4_transformers
uv sync --locked
uv run --locked example_basic.py
```

Use the same commands in `llmjp4_vllm` for its basic example. See the root README
for server startup and client commands.

Read each `pyproject.toml` and `uv.lock` before changing dependencies. The projects
have different dependency constraints. The external `llm-jp-vllm` package
integrates with vLLM's parser interfaces; its compatibility must be checked when
upgrading vLLM. Do not assume the two environments are interchangeable.
For an intentional dependency change, update the affected manifest and regenerate
its lockfile with `uv lock` in that directory. Keep unrelated lockfiles unchanged.

The Transformers examples require Transformers 5.0.0 or later for `parse_response`.

The vLLM project requires vLLM 0.30.0 or later and `llm-jp-vllm` 0.1.1 or later
from PyPI. Keep the minimum versions and lockfile consistent, and check parser
compatibility when upgrading either package.

LLM-jp-4.1 GGUF models require upstream llama.cpp v0.6.0 or later for the
Harmony chat parser. Document minimum stable releases, excluding pre-releases.

## Implementation guidance

- Follow the existing Python style and keep runnable examples behind a
  `main()` function and `if __name__ == "__main__"` guard.
- Preserve the bundled tokenizer and `trust_remote_code` settings unless the
  task explicitly changes how model code is loaded.
- Use `llm_jp_vllm.llmjp4.harmony.HarmonyMessageParser` for vLLM token parsing.
  Its message sections are token-ID lists, and `start_position` is the message
  offset. Keep parser implementations in the external library rather than
  copying them into this cookbook. The Transformers example uses the model's
  bundled parser, whose section objects have a different API.
- Preserve the assistant prefill where a caller reconstructs a full Harmony
  message from generated tokens. Generated IDs can omit prompt tokens.
- Decode vLLM output with the model tokenizer. The basic example documents
  whitespace issues with `output.text`.
- Start servers with the standard `vllm serve` command and
  `--reasoning-parser llmjp4 --reasoning-parser-plugin llm_jp_vllm.llmjp4`.
  No local CLI wrapper or parser-registration module is needed.
- Keep model names and endpoints consistent across server commands and
  both `curl_*.sh` clients when changing defaults. Update user documentation when
  commands or observable behavior change.
- Keep changes focused on the requested feature or fix. Avoid speculative
  abstractions, unrelated refactors, and unnecessary dependencies.

## Validation

Choose checks that match the change. For documentation-only changes, check local
links, paths, command working directories, and consistency with the source; model
downloads and inference are unnecessary.

For Python or shell changes, these basic syntax checks can be run from the
repository root with Python 3.13 or later available as `python3`:

```bash
python3 -m py_compile llmjp4_transformers/*.py llmjp4_vllm/*.py
bash -n llmjp4_vllm/curl_chat_test.sh
bash -n llmjp4_vllm/curl_function_calling_test.sh
git diff --check
```

Syntax checks do not validate dependency compatibility or inference. When the
relevant environment and hardware are available:

- Run the affected `example_basic.py` using that runtime's environment. Inspect
  generated tokens, decoded text, and parsed messages.
- For vLLM dependency or serving changes, start `vllm serve` with the documented
  plugin options and run both `curl_*.sh` clients from another terminal. Inspect
  reasoning, final-answer, and tool-call deltas, and check non-streaming requests.
  The shell script is a manual request, not an automated assertion suite.
- For changes to the Harmony example, check the external parser's message API
  and assistant-prefill handling. Parser implementation fixes belong in
  [llm-jp-vllm](https://github.com/llm-jp/llm-jp-vllm).
- For llama.cpp documentation changes, check consistency with the documented
  upstream release and distinguish commands inspected from commands actually
  executed.

Report the checks performed and any validation that could not be run. Do not
claim inference passed based only on syntax checks or the recorded test environment.

## Planning and review

Implementation proposals should be self-contained: explain the repository
context and problem before describing concrete changes. Link references to the
specific sections needed to understand the proposal, and avoid proposing work
that is unnecessary for the requested outcome.

Share review findings in the session before posting any approval, change
request, or comment to GitHub. Post only content explicitly agreed with the user.
Where applicable, group observations into blockers, non-blockers, questions,
positive findings, and out-of-scope discoveries. Distinguish observations from
the changes actually required for the current pull request. Track separate
problems in separate issues rather than expanding the current review, and keep
acceptance criteria proportional to the change.

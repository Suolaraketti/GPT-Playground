# CLAUDE.md — GPT-Playground

This file provides guidance to AI assistants (Claude, Copilot, etc.) working in this repository. Read it before making any changes.

---

## Project Overview

**GPT-Playground** is an experimentation and prototyping repository for working with large language model (LLM) APIs. It serves as a sandbox for testing prompts, building small AI-powered utilities, comparing model outputs, and developing reusable patterns for LLM integration.

> This repository was initialized empty. As the project grows, update this file to reflect the actual structure, conventions, and workflows.

---

## Repository Structure (Expected)

```
GPT-Playground/
├── CLAUDE.md              # This file
├── README.md              # Human-readable project overview
├── .env.example           # Template for required environment variables
├── .gitignore             # Files excluded from version control
├── src/                   # Source code
│   ├── prompts/           # Prompt templates and experiments
│   ├── utils/             # Shared utility functions
│   └── examples/          # Standalone example scripts
├── tests/                 # Test files mirroring src/ structure
├── docs/                  # Additional documentation
└── scripts/               # Developer helper scripts
```

Update this section as the actual structure is established.

---

## Technology Stack

Document the stack here as it is chosen. Common choices for an LLM playground:

| Layer | Candidate Technologies |
|---|---|
| Language | TypeScript / Python |
| AI SDK | Anthropic SDK, OpenAI SDK |
| Testing | Jest / Vitest (TS), pytest (Python) |
| Linting | ESLint + Prettier (TS), ruff (Python) |
| Runtime | Node.js ≥ 18 / Python ≥ 3.11 |

---

## Environment Variables

All secrets and API keys **must** be kept out of version control. Use a `.env` file locally (never commit it) and populate it from `.env.example`.

```bash
# Copy the template and fill in your values
cp .env.example .env
```

Expected variables (add to `.env.example` as they are needed):

```bash
# AI Provider Keys
ANTHROPIC_API_KEY=         # Anthropic / Claude
OPENAI_API_KEY=            # OpenAI / GPT

# Optional configuration
MODEL_DEFAULT=             # Default model to use (e.g. claude-opus-4-6)
LOG_LEVEL=info             # debug | info | warn | error
```

**Rules for AI assistants:**
- Never hardcode API keys or secrets in source files.
- Never commit `.env` — always commit `.env.example` with placeholders.
- Read secrets from `process.env` (Node) or `os.environ` (Python).

---

## Development Workflow

### Getting Started

```bash
# 1. Clone the repository
git clone <repo-url>
cd GPT-Playground

# 2. Install dependencies (update command to match your stack)
npm install          # Node/TypeScript
# or
pip install -r requirements.txt  # Python

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run the project
npm run dev          # or python src/main.py
```

### Branching Strategy

- `main` — stable, reviewed code only. Never push directly.
- `claude/<description>-<id>` — AI-generated feature branches.
- `feat/<description>` — human-authored feature branches.
- `fix/<description>` — bug fix branches.

All changes go through pull requests. Branch names should be descriptive.

### Commits

Use conventional commit messages:

```
feat: add prompt chaining utility
fix: handle rate limit retries correctly
docs: update CLAUDE.md with new structure
refactor: extract model config to separate module
test: add unit tests for token counting helper
chore: update dependencies
```

---

## Code Conventions

### General

- Keep files small and focused on a single responsibility.
- Prefer explicit over implicit — avoid magic values; define named constants.
- All functions and modules that interact with external APIs must handle errors gracefully (network failures, rate limits, invalid responses).
- Do not add unnecessary comments. Code should be self-documenting; add comments only where the intent is non-obvious.

### TypeScript (if used)

- Strict mode (`"strict": true`) in `tsconfig.json`.
- Prefer `const` over `let`; avoid `var`.
- Use named exports; avoid default exports unless required by a framework.
- All async functions must be `await`ed or returned — never fire-and-forget.
- Run `npm run lint` and `npm run typecheck` before committing.

### Python (if used)

- Format with `ruff format` or `black`.
- Lint with `ruff check` or `flake8`.
- Type annotations required for all function signatures.
- Use `python-dotenv` to load `.env` files.
- Run `pytest` before committing.

---

## Testing

Write tests for all non-trivial logic. Tests live in `tests/` and mirror the `src/` structure.

```bash
# Run all tests
npm test             # Node/TypeScript
pytest               # Python

# Run with coverage
npm run test:coverage
pytest --cov=src
```

**Guidelines:**
- Unit tests for pure functions (no API calls).
- Integration tests that call real APIs should be marked (e.g., `@pytest.mark.integration`) and opt-in only.
- Mock external API calls in unit tests to avoid costs and flakiness.
- Tests must pass before merging any PR.

---

## Working with AI APIs

### Rate Limits and Retries

Always implement retry logic with exponential backoff for API calls:

```typescript
// TypeScript example pattern
async function callWithRetry(fn: () => Promise<unknown>, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      await sleep(Math.pow(2, attempt) * 1000); // 1s, 2s, 4s
    }
  }
}
```

### Cost Awareness

- Log token usage for every API call during development.
- Prefer smaller/faster models for iteration; use larger models for final outputs.
- Use prompt caching where supported (Anthropic) to reduce costs on repeated prefixes.
- Never run expensive bulk experiments without reviewing estimated costs first.

### Prompt Management

- Store reusable prompt templates in `src/prompts/` as separate files, not inline strings.
- Version prompts meaningfully — small changes can significantly affect output.
- Document what each prompt is designed to do and what model it was tested with.

---

## Security

- **No secrets in code.** API keys, tokens, and credentials belong in `.env` only.
- **No user-controlled input directly in prompts** without sanitization — guard against prompt injection.
- **No `eval()`** or dynamic code execution from model outputs without sandboxing.
- Regularly rotate API keys. If a key is accidentally committed, rotate it immediately and rewrite git history.

---

## AI Assistant Instructions

When working in this repository, follow these rules:

1. **Read before writing.** Always read existing files before modifying them.
2. **Minimal changes.** Only change what is necessary to complete the task. Do not refactor unrelated code.
3. **No unnecessary files.** Do not create documentation, example files, or boilerplate unless explicitly asked.
4. **Honest about uncertainty.** If the project structure is unclear, explore and ask rather than assume.
5. **Branch discipline.** All changes go on the designated feature branch. Never push to `main`.
6. **Update this file.** If you make structural changes (new top-level directories, new conventions, new dependencies), update this CLAUDE.md to reflect them.
7. **Test your changes.** Run available tests and linters before marking a task complete.

---

## Updating This File

This file should be updated whenever:

- The project stack is finalized or changed.
- New top-level directories are added.
- New required environment variables are introduced.
- Conventions or workflows change.
- A new developer (human or AI) would need different context to contribute effectively.

---

*Last updated: 2026-02-21 — Initial creation for empty repository.*

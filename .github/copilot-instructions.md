# GitHub Copilot Instructions

All AI assistance in this repository must strictly adhere to:
- [AGENTS.md](../AGENTS.md)
- [INITIAL_AGENT_INSTRUCTIONS.md](../INITIAL_AGENT_INSTRUCTIONS.md)

Key Invariants:
1. Anti-Drift & Scope Lockdown: touch only files directly required for the user prompt. Do not refactor unrelated code.
2. Strict No Emojis across all code, comments, docs, logs, and commit messages.
3. Strict No Em-Dashes: use hyphens, commas, or colons.
4. Port Safety: use port 5001 for backend, port 3000 for frontend (port 5000 is reserved on macOS).
5. No Inline Python: use dedicated scripts instead of python3 -c commands.

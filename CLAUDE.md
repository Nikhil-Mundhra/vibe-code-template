# Claude Code Instructions

Always read and strictly adhere to:
1. [AGENTS.md](AGENTS.md): Canonical directives, communication rules, typography invariants, and runtime guardrails.
2. [INITIAL_AGENT_INSTRUCTIONS.md](INITIAL_AGENT_INSTRUCTIONS.md): Step-by-step onboarding protocol, skill trimming, and template acquisition rules.

## Core Non-Negotiable Invariants
- Anti-Drift & Scope Lockdown: Touch only files directly in the blast radius of the prompt. Do not refactor unrelated code.
- Strict No Emojis: Never use Unicode emojis in copy, code, logs, or git commits. Use textual badges ([INFO], [PASS], [FAIL]).
- Strict No Em-Dashes: Never use em-dashes. Use hyphens, commas, or colons instead.
- Port Safety: macOS port 5000 is occupied by AirPlay. Use port 5001 for backend servers, port 3000 for frontend.
- No Inline Python: Never run python inline via terminal (-c). Write a script in scratch/ instead.

# CLAUDE.md

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Write detailed specs upfront to reduce ambiguity
- **PM-Oriented Plans**: Plans describe WHAT the user sees and does, not HOW the code works. Structure as: user goal → interaction flow → acceptance criteria → edge cases. No function names, file paths, or implementation details unless explicitly asked.
- Write plan to `tasks/todo.md` with checkable items. Check in before starting implementation.

### 2. Autonomous Execution
- Once plan is confirmed, execute end-to-end with zero hand-holding. Request all necessary permissions upfront in one batch — do not prompt per-file or per-command.
- Mark `tasks/todo.md` items complete as you go. Summarize each step by what changed for the user, not what changed in the code.
- When given a bug report: just fix it. Point at logs, errors, failing tests — then resolve them. Go fix failing CI tests without being told how.

### 3. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- One task per subagent for focused execution

### 4. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Review lessons at session start for relevant project

### 5. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 6. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer

### 7. Auto-Commit & PR Workflow
- After completing each feature/fix, automatically stage, commit, and push to a feature branch
- Branch naming: `feat/<short-description>` or `fix/<short-description>`
- Commit messages: concise Chinese, imperative mood
- **One logical change per PR** — do not bundle unrelated changes
- After push, create PR with: title, description (why + what the user sees), test notes
- Always run lint/test BEFORE committing. Never push broken code.

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
- Prefer action over clarification — make reasonable assumptions and proceed
- Always check local config and project files before searching the web or asking me for information.
- Add at the top of CLAUDE.md under a ## General Behavior section so it applies globally to all interactions.\n\nWhen I ask you to do something, start doing it immediately. Do not ask clarifying questions unless you truly cannot proceed. Prefer action over planning — make your best guess and I'll correct you if needed.
- Add under a ## MCP & Tools section in CLAUDE.md.\n\nAlways check local MCP server configurations (`.claude/settings.json`, project settings) before searching the web or asking me which tools/servers are available.
- Add under a ## Project Structure section in CLAUDE.md.\n\nIn this project, skill files and scripts should use a skill-local directory layout — place extracted scripts and references inside the skill's own directory, not in plugin-wide directories.

# Evaluation fixture

Use `java-repository/` as the identical initial content for every evaluation
variant. For each independent run:

1. Copy the directory to a fresh location.
2. Initialize Git, configure a local test identity, add all files and create an
   initial commit.
3. Apply exactly one prompt from `tasks.md`.
4. Run the Baseline, Static and MCP variants described in
   `../evaluation-plan.md` in separate Codex sessions.
5. Record the trace and resulting repository in `../results-template.md`.

Do not reuse a worktree or agent session between variants.


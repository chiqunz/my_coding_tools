# dev-loop

AI-driven development loop: automated bug discovery, prompt auditing, issue triage, and implementation — fully driven by `claude -p` + cron.

## Quick Start

### 1. Prerequisites

- **Claude Code CLI** (`claude`) — installed and on PATH
- **LiteLLM proxy** — running via [mai-agents](https://github.com/infinity-microsoft/mai-agents) `setup.sh`
- **GitHub CLI** (`gh`) — authenticated with read/write access to issues and PRs
- **jq** — for JSON parsing in shell scripts
- No `flock` needed — scripts use `mkdir`-based locking (works natively on macOS and Linux)

### 2. Copy the plugin into your target repo

```bash
cd /path/to/your-repo          # e.g. ~/Work/Repo/maibot

# Copy both directories
cp -r /path/to/overagents/.claude .claude
cp -r /path/to/overagents/scripts scripts

# Create logs directory
mkdir -p logs

# Make scripts executable
chmod +x scripts/*.sh .claude/scripts/*.sh
```

Your repo should now have:

```
your-repo/
├── .claude/          # Agent definitions, routines, hooks, skills
├── scripts/          # Shell scripts to run each stage
└── logs/             # Created above, populated at runtime
```

### 3. Make sure LiteLLM proxy is running

The scripts use your [mai-agents](https://github.com/infinity-microsoft/mai-agents) LiteLLM proxy — no Anthropic API key needed.

```bash
# If you haven't already, run mai-agents setup
cd ~/Work/Repo/mai-agents
./setup.sh

# Verify the proxy is healthy
curl -sf http://localhost:4000/health/liveness && echo "OK"
```

The scripts look for the mai-agents `.env` file at `~/Work/Repo/mai-agents/.run/.env-*` by default.
If yours is elsewhere, set `MAI_AGENTS_DIR` in your environment or at the top of each script.

### 4. Verify everything works

```bash
cd /path/to/your-repo

# Check prerequisites
gh auth status
claude --version
echo '{"test":true}' | jq .

# Smoke test — run triage (safe, read-only if no issues exist)
./scripts/run-triage.sh
tail -f logs/triage.log
```

### 5. Run stages manually

```bash
cd /path/to/your-repo

./scripts/run-bug-scanner.sh      # Stage 1: discover bugs
./scripts/run-prompt-auditor.sh   # Stage 2: audit prompts
./scripts/run-triage.sh           # Stage 3: validate pending issues
./scripts/run-implement.sh        # Stage 4: implement next triage issue
```

### 6. (Optional) Schedule with cron

```cron
# Stage 1: Bug scanner — nightly at 2 AM
0 2 * * * cd /path/to/your-repo && ./scripts/run-bug-scanner.sh

# Stage 2: Prompt auditor — nightly at 3 AM
0 3 * * * cd /path/to/your-repo && ./scripts/run-prompt-auditor.sh

# Stage 3: Triage / validator — every hour on the hour
0 * * * * cd /path/to/your-repo && ./scripts/run-triage.sh

# Stage 4: Implementer — every hour at :30
30 * * * * cd /path/to/your-repo && ./scripts/run-implement.sh
```

If your mai-agents is not at the default path (`~/Work/Repo/mai-agents`), set `MAI_AGENTS_DIR` before each command.

## How It Works

GitHub Issues are the only shared state between all stages. Labels act as a state machine driving issues through the pipeline. Every stage is independently idempotent — no direct inter-process communication.

```
┌──────────────────┬───────────────────┬───────────────────────────┐
│  DISCOVERY       │  TRIAGE           │  IMPLEMENT                │
│  (cron, nightly) │  (cron, hourly)   │  (cron, hourly+30min)     │
│                  │                   │                           │
│  bug-scanner     │  issue-validator  │  issue-implementer        │
│  prompt-auditor  │                   │  └─ 5x code-reviewer      │
│                  │                   │     (parallel subagents)   │
└──────────────────┴───────────────────┴───────────────────────────┘
         ↓ creates Issues                      ↑ reads Issues
                   GitHub Issues = message bus
                   Labels        = state machine
```

## Pipeline Stages

### Stage 1: Bug Scanner (nightly)

Scans the entire codebase for coding bugs — null references, resource leaks, race conditions, security vulnerabilities, etc. Creates GitHub Issues with label `auto-discovered, bug`.

### Stage 2: Prompt Auditor (nightly)

Reviews all prompts, agent definitions, skill files, and AI workflow instructions for quality issues — context bloat, conflicting instructions, missing guardrails, token inefficiency. Creates issues with label `auto-discovered, prompt-quality`.

### Stage 3: Issue Validator (hourly)

Pulls all `auto-discovered` issues, re-reads the referenced code with fresh context, and independently verifies each one. Valid issues get promoted to `triage`. Invalid ones are closed with an explanation.

### Stage 4: Issue Implementer (hourly, offset by 30min)

Picks the oldest `triage` issue and implements a fix in an isolated git worktree. Before creating a PR, it MUST:

1. **Update documentation** if any public API, config, or behavior changed
2. **Run the full test suite** and ensure all tests pass
3. **Spawn 5 parallel code-reviewer subagents** (correctness, security, style, test coverage, breaking changes)
4. **Pass majority vote** — 3/5 reviewers must approve to create a PR
5. **Wait for CI to pass** before merging — if CI fails, the issue is labeled `needs-human-review`

If any gate fails, the PR is NOT created/merged and the issue is flagged for human review.

## Label State Machine

```
auto-discovered → triage → implementing → in-review → done
                    ↓                         ↓
                 invalid              needs-human-review
```

| Label | Set by | Meaning |
|---|---|---|
| `auto-discovered` | bug-scanner / prompt-auditor | Newly created, pending triage |
| `bug` | bug-scanner | Code bug category |
| `prompt-quality` | prompt-auditor | Prompt/workflow issue |
| `triage` | issue-validator | Validated, ready to implement |
| `implementing` | issue-implementer | Work in progress |
| `in-review` | issue-implementer | 5x reviewers running |
| `done` | issue-implementer | Complete |
| `invalid` | issue-validator | Closed as not actionable |
| `needs-human-review` | issue-implementer | Failed code review or CI |

## Authentication

All scripts route through a **LiteLLM proxy** provided by [mai-agents](https://github.com/infinity-microsoft/mai-agents). No direct Anthropic API key is needed.

Each script:
1. Reads `LITELLM_PROXY_URL` and `LITELLM_API_KEY` from `$MAI_AGENTS_DIR/.run/.env-*`
2. Exports them as `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY`
3. Runs `claude -p` which connects to the local proxy

| Variable | Default | Purpose |
|---|---|---|
| `MAI_AGENTS_DIR` | `~/Work/Repo/mai-agents` | Path to your mai-agents checkout |

## Observability

Logs are written to `logs/` — one file per stage:

```bash
tail -f logs/bug-scanner.log
tail -f logs/prompt-auditor.log
tail -f logs/triage.log
tail -f logs/implement.log
```

Optional tmux setup for live monitoring:

```bash
tmux new-session -d -s dev-loop
tmux new-window -t dev-loop -n bug-scanner  "tail -f logs/bug-scanner.log"
tmux new-window -t dev-loop -n triage       "tail -f logs/triage.log"
tmux new-window -t dev-loop -n implement    "tail -f logs/implement.log"
tmux attach -t dev-loop
```

## Repository Structure

```
.claude/
├── plugin.json                  # Plugin metadata
├── settings.json                # Hook configuration
├── agents/
│   ├── bug-scanner.md           # Stage 1 agent
│   ├── prompt-auditor.md        # Stage 2 agent
│   ├── issue-validator.md       # Stage 3 agent
│   ├── issue-implementer.md     # Stage 4 agent (worktree isolation)
│   └── code-reviewer.md         # Stage 4b agent (5x parallel)
├── skills/
│   ├── github-issue-ops/SKILL.md  # gh CLI wrappers: create, label, dedup
│   └── post-turn-step/SKILL.md    # Auto-runs CLAUDE.md post-turn-step
├── hooks/hooks.json             # PostToolUse → post-turn-step trigger
├── routines/
│   ├── bug-scanner.md           # Cron prompt file
│   ├── prompt-auditor.md
│   ├── issue-validator.md
│   └── issue-implementer.md
└── scripts/
    └── post-turn-step.sh        # Extracts & runs post-turn-step from CLAUDE.md

scripts/
├── run-bug-scanner.sh
├── run-prompt-auditor.sh
├── run-triage.sh
└── run-implement.sh

logs/                            # Created at runtime
```

## Safety & Cost Controls

### Concurrency

Every script uses `mkdir` as an atomic lock to prevent overlapping runs. If a stage is already running when cron fires again, the new invocation exits immediately. The lock is automatically cleaned up on exit.

### Idempotency

Every agent has explicit guards:
- **bug-scanner**: exits if no new bugs found beyond existing issues
- **issue-validator**: exits if no `auto-discovered` issues exist
- **issue-implementer**: exits if no `triage` issues exist; skips issues already labeled `implementing`, `in-review`, or `done`

### Issue Caps

Discovery agents (bug-scanner, prompt-auditor) are capped at 5 new issues per run to control noise and cost.

### Deduplication

Before creating any issue, agents semantically compare candidates against all open issues and PRs. This is judgment-based (not string matching) — Claude decides whether an existing item covers the same underlying problem.

### Quality Gates (Issue Implementer)

The implementer will NOT create a PR unless:
1. Documentation is updated (if behavior changed)
2. Full test suite passes
3. 3 of 5 code reviewers approve

The implementer will NOT merge a PR unless CI passes. Failed gates result in `needs-human-review` label.

## Worktree Isolation

Only the issue-implementer creates worktrees. All other stages are read-only.

- Branch naming: `claude/implement-YYYYMMDD-HHMMSS`
- Worktrees are stored in `../worktrees/` relative to the repo
- If the implementer makes no changes, the worktree is automatically cleaned up
- If changes are present, the worktree is preserved for review or PR creation

## Customization

### Post-Turn-Step Hook

The implementer automatically runs your project's post-turn-step after every file modification. Define it in your `CLAUDE.md`:

```markdown
## post-turn-step

```bash
npm run lint --fix
npm run typecheck
```
```

### Adjusting Models

Edit the `model:` field in the agent frontmatter files under `.claude/agents/`. Use `claude-sonnet-4-6` for cost efficiency or `claude-opus-4-6` for maximum capability.

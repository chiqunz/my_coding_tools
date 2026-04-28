# dev-loop

AI-driven development loop: automated bug discovery, prompt auditing, issue triage, and implementation — fully driven by `claude -p` + cron, billed via Anthropic API.

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

Picks the oldest `triage` issue, implements a fix in an isolated git worktree, then spawns 5 parallel code-reviewer subagents (correctness, security, style, test coverage, breaking changes). If 3/5 approve, a PR is opened automatically.

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
| `needs-human-review` | issue-implementer | Failed code review |

## Prerequisites

- **Claude CLI** (`claude`) installed and available on PATH
- **Anthropic API key** (`ANTHROPIC_API_KEY`) — all stages run via `claude -p` (headless mode), billed per token through the Anthropic Console
- **GitHub CLI** (`gh`) authenticated with read/write access to issues and PRs
- **jq** for JSON parsing in shell scripts
- **flock** for concurrency locking (`brew install flock` on macOS)

## Setup

```bash
# 1. Clone or navigate to your target repo
cd /path/to/your-repo

# 2. Copy the dev-loop plugin into your repo
cp -r /path/to/overagents/.claude .claude
cp -r /path/to/overagents/scripts scripts
mkdir -p logs

# 3. Make scripts executable
chmod +x scripts/*.sh .claude/scripts/*.sh

# 4. Verify prerequisites
gh auth status
claude --version
echo '{"test":true}' | jq .

# 5. Smoke test (manual run)
export ANTHROPIC_API_KEY=sk-ant-xxx
./scripts/run-triage.sh
tail -f logs/triage.log
```

## Cron Scheduling

Add to your crontab (`crontab -e`):

```cron
# dev-loop pipeline (source API key from a secrets file)
# Stage 1: Bug scanner — nightly at 2 AM
0 2 * * * source /etc/dev-loop-secrets && /path/to/repo/scripts/run-bug-scanner.sh

# Stage 2: Prompt auditor — nightly at 3 AM
0 3 * * * source /etc/dev-loop-secrets && /path/to/repo/scripts/run-prompt-auditor.sh

# Stage 3: Triage / validator — every hour on the hour
0 * * * * source /etc/dev-loop-secrets && /path/to/repo/scripts/run-triage.sh

# Stage 4: Implementer — every hour at :30
30 * * * * source /etc/dev-loop-secrets && /path/to/repo/scripts/run-implement.sh
```

Create `/etc/dev-loop-secrets` with `export ANTHROPIC_API_KEY=sk-ant-xxx` and `chmod 600` it.

### API Key Options

```bash
# Option A: source from a secrets file (recommended, shown above)
0 2 * * * source /etc/dev-loop-secrets && /path/to/scripts/run-bug-scanner.sh

# Option B: use a secrets manager wrapper
0 2 * * * /path/to/scripts/load-secrets-and-run.sh bug-scanner

# Option C: inline in crontab (not recommended — key visible in crontab)
0 2 * * * ANTHROPIC_API_KEY=sk-ant-xxx /path/to/scripts/run-bug-scanner.sh
```

## Manual Execution

Trigger any stage manually at any time:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx

./scripts/run-bug-scanner.sh      # discover bugs
./scripts/run-prompt-auditor.sh   # audit prompts
./scripts/run-triage.sh           # validate pending issues
./scripts/run-implement.sh        # implement next triage issue
```

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

Every script uses `flock` to prevent overlapping runs. If a stage is already running when cron fires again, the new invocation exits immediately.

### Idempotency

Every agent has explicit guards:
- **bug-scanner**: exits if no new bugs found beyond existing issues
- **issue-validator**: exits if no `auto-discovered` issues exist
- **issue-implementer**: exits if no `triage` issues exist; skips issues already labeled `implementing`, `in-review`, or `done`

### Issue Caps

Discovery agents (bug-scanner, prompt-auditor) are capped at 5 new issues per run to control noise and cost.

### Deduplication

Before creating any issue, agents semantically compare candidates against all open issues and PRs. This is judgment-based (not string matching) — Claude decides whether an existing item covers the same underlying problem.

### Cost Estimates

| Stage | Model | Est. cost/run |
|---|---|---|
| bug-scanner | Sonnet | $0.15–$0.60 |
| prompt-auditor | Sonnet | $0.09–$0.30 |
| issue-validator | Sonnet | $0.03–$0.09 |
| issue-implementer | Opus | $0.80–$4.00 |
| 5x code-reviewer | Sonnet | $0.06–$0.24 each |

**Estimated monthly total: ~$120–540** depending on repo size and activity.

Set a spend cap in the [Anthropic Console](https://console.anthropic.com) under Settings → Billing → Spend Limits.

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

### Targeting a Different Repo

Update the `REPO_DIR` variable at the top of each script in `scripts/`, or set it via environment variable.

### Adjusting Models

Edit the `model:` field in the agent frontmatter files under `.claude/agents/`. Use `claude-sonnet-4-6` for cost efficiency or `claude-opus-4-6` for maximum capability.

---
name: github-issue-ops
description: >
  Use when creating, labeling, closing, or deduplicating GitHub Issues.
  Provides standardized gh CLI patterns for all dev-loop agents.
---

# GitHub Issue Operations

## Deduplication Check

Before creating ANY issue, you MUST run this deduplication check:

1. Fetch all open issues:
   ```bash
   gh issue list --state open --json number,title,body,labels
   ```

2. Fetch all open PRs:
   ```bash
   gh pr list --state open --json number,title,body
   ```

3. For each candidate issue, semantically compare against all open issues and PRs:
   - Ask: "Does any existing open issue or PR cover the same underlying problem?"
   - This is SEMANTIC judgment, not string matching
   - If there's substantial overlap → skip creation
   - If there's partial overlap → create with a reference to the related issue/PR

## Creating Issues

Use this template:
```bash
gh issue create \
  --title "[type]: [concise description]" \
  --body "## Summary
[2-3 sentence description]

## Affected Files
- path/to/file.ext:L<line>

## Severity
[High/Medium/Low — with brief justification]

## Discovered by
dev-loop/[agent-name] on $(date)" \
  --label "[labels]"
```

Types: `bug:` for code bugs, `prompt:` for prompt quality issues.

## Label Operations

```bash
# Add labels
gh issue edit <NUMBER> --add-label "label1,label2"

# Remove labels
gh issue edit <NUMBER> --remove-label "label1"

# Combined
gh issue edit <NUMBER> --remove-label "old-label" --add-label "new-label"
```

## Closing Issues

Always close with a comment explaining why:
```bash
gh issue close <NUMBER> --comment "[explanation]"
gh issue edit <NUMBER> --add-label "invalid"
```

## Label Reference

| Label | Set by | Meaning |
|---|---|---|
| `auto-discovered` | bug-scanner / prompt-auditor | Newly created, pending triage |
| `bug` | bug-scanner | Code bug category |
| `prompt-quality` | prompt-auditor | Prompt/workflow issue |
| `triage` | issue-validator | Validated, ready to implement |
| `implementing` | issue-implementer | Work in progress |
| `in-review` | issue-implementer | Reviewers running |
| `done` | issue-implementer | Complete |
| `invalid` | issue-validator | Closed as not actionable |
| `needs-human-review` | issue-implementer | Failed code review |

#!/usr/bin/env bash
set -euo pipefail

for ((i=1; i<=30; i++)); do
  claude --dangerously-skip-permissions "Use quant-strategy-miner skill to mine useful quant trading strategy based on price and volume data. The trading frequency should be mid term (holding several days at least), no intra-day trading. Write your mined strategy into a markdown file."
  sleep 60
done

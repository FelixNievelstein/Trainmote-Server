#!/usr/bin/env bash
# Prüft, dass ein PR höchstens MAX_LINES Zeilen ändert (added + deleted).
# Ausgenommen: package-lock.json, generierte Prisma-Migrationen, reine Löschungs-PRs.
# Aufruf: scripts/check-diff-size.sh [base-ref]   (Standard: origin/develop)
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

BASE="${1:-origin/develop}"
MAX_LINES="${MAX_LINES:-300}"

stats="$(git diff --numstat "${BASE}...HEAD" -- . \
  ':(exclude,glob)**/package-lock.json' \
  ':(exclude,glob)**/prisma/migrations/**/migration.sql')"

added=0
deleted=0
while read -r a d _file; do
  [[ -z "${a:-}" || "$a" == "-" ]] && continue
  added=$((added + a))
  deleted=$((deleted + d))
done <<< "$stats"

total=$((added + deleted))
echo "Geänderte Zeilen gegenüber ${BASE}: +${added} -${deleted} = ${total} (Limit ${MAX_LINES})"

if [[ "$added" -eq 0 ]]; then
  echo "Reine Löschung, Limit gilt nicht."
  exit 0
fi

if [[ "$total" -gt "$MAX_LINES" ]]; then
  echo "FEHLER: PR ist zu groß. Bitte in kleinere PRs aufteilen." >&2
  exit 1
fi

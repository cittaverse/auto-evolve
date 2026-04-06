# ClawHub 500 Weekly Release v2026.13

**Date**: 2026-03-25 07:36-07:50 UTC
**Task**: Weekly release cron job (d2f5f4c9)

## What Happened

Executed ClawHub 500 Week 13 release — the **first real AI evaluation**.

### Key Results

1. **AI Evaluation**: 600 skills scored by qwen3-coder-plus (Bailian API), 100% success (60/60 batches)
2. **Average Score**: 62.3 (up from 45.0 mock baseline) — real differentiation achieved
3. **Score Distribution**:
   - Keep (70-89): 229 skills (38.2%)
   - Watch (50-69): 236 skills (39.3%)
   - Downgrade (<50): 135 skills (22.5%)
   - No upgrades (max score 88, threshold 90)
4. **Top Skills** (88 pts): docling, pyright-lsp, arc-security-mcp, yoder-skill-auditor, secrets-management, arc-workflow-orchestrator
5. **Bottom Skills**: ai-remote-viewing-ai-isbe (20), aetherlang (25)

### Release Artifacts

- **Git Tag**: v2026.13
- **GitHub Release**: https://github.com/cittaverse/clawhub-500/releases/tag/v2026.13
- **Release Notes**: WEEKLY-RELEASE-v2026.13.md
- **Quality Dashboard**: Updated with real data
- **Reevaluation Data**: data/reevaluation-2026-03-25.json (10K+ lines)

### Infrastructure Changes

- Merged `weekly-reeval-2026-03-25` branch into main
- New script: `scripts/weekly-reevaluation-fast.py` (10x faster batch eval)
- Security: credential leak fixed (.gitignore hardened)

### Observations

- **Upgrade threshold may be too high**: Max score is 88, but upgrade requires ≥90. Consider adjusting to ≥85 next cycle.
- **135 downgrade candidates**: Need review — some are clearly junk (asdasdas123), others may be niche but valid.
- **No new skills this week**: Collection stable at 600.

### Next Steps (v2026.14)

1. Review downgrade candidates for removal
2. Calibrate scoring thresholds
3. Integrate VirusTotal security scanning
4. Consider lowering upgrade threshold to ≥85

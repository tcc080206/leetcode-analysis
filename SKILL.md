---
name: leetcode-analysis
description: Analyze a LeetCode user's progress by fetching solved problems, generating a report, and providing personalized recommendations. Use when the user asks about LeetCode progress, interview readiness, weak topics, or wants to analyze their LeetCode profile.
---

# LeetCode Progress Analysis

## Prerequisites

- Python 3 with `urllib` (standard library, no extra packages needed)
- The user must provide their LeetCode username

## Workflow

1. **Get the username** — if the user hasn't provided a LeetCode username, ask for it before proceeding.

2. **Run the analysis script** — the script is in the `scripts/` subdirectory of this skill's installation folder. Determine the correct path based on where this skill is installed:

   - Cursor: `~/.cursor/skills/leetcode-analysis/scripts/leetcode_analysis.py`
   - Claude Code: `~/.claude/skills/leetcode-analysis/scripts/leetcode_analysis.py`

```bash
python3 <SKILL_DIR>/scripts/leetcode_analysis.py <username>
```

The script outputs the report path to stdout (e.g. `/tmp/leetcode_report_<username>.md`). Status messages go to stderr. Wait up to 60 seconds — the API can be slow on cold starts.

3. **Read the generated report** — read the `.md` file from the path printed by the script.

4. **Analyze and respond in Traditional Chinese (繁體中文)** — summarize the report and provide insights covering:

   - **Difficulty distribution**: compare Easy/Medium/Hard ratio to the ideal (20/60/20) and flag imbalances
   - **Topic coverage**: highlight strong areas, flag weak/missing topics with specific problem recommendations
   - **Accept rate & beats percentage**: note quality of solutions
   - **Contest performance**: if available, assess competitive standing
   - **Interview readiness score**: explain the scoring breakdown and what to improve
   - **Prioritized action plan**: give concrete next steps with specific problem links

5. **Invite follow-up questions** — tell the user they can ask deeper questions about any section, request practice plans for specific topics, or compare progress over time.

## Analysis Guidelines

When interpreting the report data, apply these heuristics:

| Metric | Threshold | Interpretation |
|--------|-----------|---------------|
| Total solved | 300+ | Solid foundation for interviews |
| Hard ratio | < 12% | Needs more Hard practice |
| Topic benchmark ratio | >= 1.5x | Strong |
| Topic benchmark ratio | 1.0x - 1.5x | Adequate |
| Topic benchmark ratio | < 1.0x | Weak — recommend specific problems |
| Beats percentage | > 90% | Excellent solution quality |
| Contest rating | > 1800 | Strong competitive ability |

## Example Follow-up Prompts

Users may ask things like:

- "DP 我該怎麼加強？推薦我一個練習計畫"
- "我想準備 Google 面試，還缺什麼？"
- "幫我比較上次的報告，看我有沒有進步"
- "Hard 題我該從哪個主題開始刷？"
- "我的 Graph 相關題目夠嗎？"

For these, reference the report data and give specific, actionable advice with LeetCode problem links.

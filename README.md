# LeetCode Progress Analyzer

An AI agent skill that analyzes your LeetCode profile and delivers a personalized progress report with actionable recommendations — all in Traditional Chinese.

一個 AI agent skill，分析你的 LeetCode 刷題進度，產出個人化報告與具體建議。

## Features / 功能

- Difficulty distribution analysis (Easy / Medium / Hard ratio vs. ideal 20/60/20)
- Topic coverage across 30+ core interview topics with benchmark comparisons
- Accept rate & beats percentage evaluation
- Contest performance summary (if available)
- Interview readiness score (0–100) with category breakdown
- Weak area identification with recommended problems and direct links
- Prioritized action plan

## Prerequisites / 前置需求

- **Python 3** (uses only standard library — no `pip install` needed)
- A **public** LeetCode profile

## Installation / 安裝

Clone this repo into your AI tool's skill directory.

將此 repo clone 到你使用的 AI 工具的 skill 資料夾。

### Cursor

```bash
git clone https://github.com/tcc080206/leetcode-analysis.git ~/.cursor/skills/leetcode-analysis
```

### Claude Code

```bash
git clone https://github.com/tcc080206/leetcode-analysis.git ~/.claude/skills/leetcode-analysis
```

### Verify installation / 驗證安裝

```bash
python3 ~/.cursor/skills/leetcode-analysis/scripts/leetcode_analysis.py --help
# or for Claude Code:
python3 ~/.claude/skills/leetcode-analysis/scripts/leetcode_analysis.py --help
```

If you see `Usage: leetcode_analysis.py <username>`, you're all set.

## Usage / 使用方式

Once installed, just talk to your AI agent in natural language. The skill activates automatically when it detects LeetCode-related requests.

安裝完成後，直接用自然語言跟 AI 對話即可。skill 會在偵測到 LeetCode 相關請求時自動啟動。

### Getting started / 開始分析

Simply ask:

```
分析我的 LeetCode，我的帳號是 <username>
```

```
Analyze my LeetCode progress, username: <username>
```

The agent will fetch your public data from LeetCode, generate a detailed report, and present the analysis.

### Follow-up questions / 後續可以問的問題

After the initial analysis, you can dive deeper:

| Question | What you get |
|----------|-------------|
| `DP 我該怎麼加強？推薦我一個練習計畫` | Targeted DP practice plan with specific problems |
| `我想準備 Google 面試，還缺什麼？` | Gap analysis against big-tech interview expectations |
| `幫我比較上次的報告，看我有沒有進步` | Progress comparison across reports |
| `Hard 題我該從哪個主題開始刷？` | Prioritized Hard problem recommendations by topic |
| `我的 Graph 相關題目夠嗎？` | Deep-dive on a specific topic's coverage |
| `幫我排一個兩週的刷題計畫` | Structured study plan based on your weak areas |
| `我的 accept rate 怎麼提升？` | Tips on improving solution quality |

## How it works / 運作原理

```
You: "分析我的 LeetCode"
 │
 ▼
AI Agent reads SKILL.md
 │
 ▼
Python script queries LeetCode GraphQL API
 │
 ▼
Markdown report saved to /tmp/leetcode_report_<username>.md
 │
 ▼
AI reads report & delivers personalized analysis (繁體中文)
```

The Python script uses only LeetCode's public GraphQL API — no authentication or API key required. Results are cached for 30 minutes to avoid rate limiting.

## File structure / 檔案結構

```
leetcode-analysis/
├── SKILL.md                        # Agent instructions (read by AI)
├── README.md                       # This file (for humans)
└── scripts/
    └── leetcode_analysis.py        # Data fetcher & report generator
```

## License

MIT

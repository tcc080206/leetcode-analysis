#!/usr/bin/env python3
"""LeetCode Progress Analyzer — fetches public data and produces a Markdown report."""

import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

GRAPHQL_URL = "https://leetcode.com/graphql/"
CACHE_SCHEMA_VERSION = 1
CACHE_TTL_SECONDS = 30 * 60
MAX_RETRIES = 4

LEETCODE_TOTAL = {"EASY": 830, "MEDIUM": 1750, "HARD": 850}

CORE_INTERVIEW_TOPICS = [
    "Array", "String", "Hash Table", "Dynamic Programming", "Binary Search",
    "Tree", "Binary Tree", "Graph Theory", "Depth-First Search",
    "Breadth-First Search", "Stack", "Queue", "Linked List", "Greedy",
    "Backtracking", "Sliding Window", "Two Pointers", "Union-Find", "Trie",
    "Bit Manipulation", "Sorting", "Math", "Design", "Monotonic Stack",
    "Divide and Conquer", "Recursion", "Matrix", "Topological Sort",
    "Shortest Path", "Segment Tree", "Binary Indexed Tree",
]

TOPIC_BENCHMARKS = {
    "Array": 80, "String": 40, "Hash Table": 40, "Dynamic Programming": 40,
    "Binary Search": 25, "Tree": 25, "Binary Tree": 25, "Graph Theory": 20,
    "Depth-First Search": 30, "Breadth-First Search": 25, "Stack": 20,
    "Queue": 10, "Linked List": 20, "Greedy": 25, "Backtracking": 15,
    "Sliding Window": 15, "Two Pointers": 25, "Union-Find": 10, "Trie": 8,
    "Bit Manipulation": 15, "Sorting": 25, "Math": 20, "Design": 15,
    "Monotonic Stack": 8, "Divide and Conquer": 10, "Recursion": 10,
    "Matrix": 15, "Topological Sort": 5, "Shortest Path": 5,
    "Segment Tree": 5, "Binary Indexed Tree": 5,
}

RECOMMENDED_PROBLEMS = {
    "Queue": [
        ("232", "Implement Queue using Stacks", "Easy"),
        ("622", "Design Circular Queue", "Medium"),
        ("641", "Design Circular Deque", "Medium"),
        ("862", "Shortest Subarray with at Least K", "Hard"),
        ("239", "Sliding Window Maximum", "Hard"),
    ],
    "Recursion": [
        ("509", "Fibonacci Number", "Easy"),
        ("50", "Pow(x, n)", "Medium"),
        ("779", "K-th Symbol in Grammar", "Medium"),
        ("894", "All Possible Full Binary Trees", "Medium"),
    ],
    "Trie": [
        ("208", "Implement Trie (Prefix Tree)", "Medium"),
        ("211", "Design Add and Search Words", "Medium"),
        ("212", "Word Search II", "Hard"),
        ("648", "Replace Words", "Medium"),
        ("1268", "Search Suggestions System", "Medium"),
    ],
    "Topological Sort": [
        ("207", "Course Schedule", "Medium"),
        ("210", "Course Schedule II", "Medium"),
        ("269", "Alien Dictionary", "Hard"),
        ("310", "Minimum Height Trees", "Medium"),
        ("802", "Find Eventual Safe States", "Medium"),
    ],
    "Shortest Path": [
        ("743", "Network Delay Time", "Medium"),
        ("787", "Cheapest Flights Within K Stops", "Medium"),
        ("1514", "Path with Maximum Probability", "Medium"),
        ("1631", "Path With Minimum Effort", "Medium"),
        ("778", "Swim in Rising Water", "Hard"),
    ],
    "Sliding Window": [
        ("567", "Permutation in String", "Medium"),
        ("438", "Find All Anagrams in a String", "Medium"),
        ("76", "Minimum Window Substring", "Hard"),
        ("904", "Fruit Into Baskets", "Medium"),
        ("1004", "Max Consecutive Ones III", "Medium"),
    ],
    "Graph Theory": [
        ("133", "Clone Graph", "Medium"),
        ("399", "Evaluate Division", "Medium"),
        ("785", "Is Graph Bipartite?", "Medium"),
        ("1192", "Critical Connections in a Network", "Hard"),
        ("684", "Redundant Connection", "Medium"),
    ],
    "Backtracking": [
        ("46", "Permutations", "Medium"),
        ("78", "Subsets", "Medium"),
        ("51", "N-Queens", "Hard"),
        ("37", "Sudoku Solver", "Hard"),
        ("131", "Palindrome Partitioning", "Medium"),
    ],
    "Dynamic Programming": [
        ("1143", "Longest Common Subsequence", "Medium"),
        ("72", "Edit Distance", "Medium"),
        ("312", "Burst Balloons", "Hard"),
        ("10", "Regular Expression Matching", "Hard"),
        ("188", "Best Time to Buy and Sell Stock IV", "Hard"),
    ],
    "Segment Tree": [
        ("307", "Range Sum Query - Mutable", "Medium"),
        ("315", "Count of Smaller Numbers After Self", "Hard"),
        ("493", "Reverse Pairs", "Hard"),
        ("699", "Falling Squares", "Hard"),
    ],
    "Binary Indexed Tree": [
        ("307", "Range Sum Query - Mutable", "Medium"),
        ("315", "Count of Smaller Numbers After Self", "Hard"),
        ("327", "Count of Range Sum", "Hard"),
    ],
    "Monotonic Stack": [
        ("496", "Next Greater Element I", "Easy"),
        ("503", "Next Greater Element II", "Medium"),
        ("84", "Largest Rectangle in Histogram", "Hard"),
        ("42", "Trapping Rain Water", "Hard"),
        ("907", "Sum of Subarray Minimums", "Medium"),
    ],
    "Design": [
        ("146", "LRU Cache", "Medium"),
        ("460", "LFU Cache", "Hard"),
        ("380", "Insert Delete GetRandom O(1)", "Medium"),
        ("295", "Find Median from Data Stream", "Hard"),
        ("716", "Max Stack", "Hard"),
    ],
    "Union-Find": [
        ("547", "Number of Provinces", "Medium"),
        ("684", "Redundant Connection", "Medium"),
        ("721", "Accounts Merge", "Medium"),
        ("990", "Satisfiability of Equality Equations", "Medium"),
        ("1319", "Number of Operations to Make Network Connected", "Medium"),
    ],
    "Hard General": [
        ("4", "Median of Two Sorted Arrays", "Hard"),
        ("23", "Merge k Sorted Lists", "Hard"),
        ("25", "Reverse Nodes in k-Group", "Hard"),
        ("41", "First Missing Positive", "Hard"),
        ("124", "Binary Tree Maximum Path Sum", "Hard"),
        ("297", "Serialize and Deserialize Binary Tree", "Hard"),
        ("329", "Longest Increasing Path in a Matrix", "Hard"),
        ("239", "Sliding Window Maximum", "Hard"),
    ],
}


def _safe_username(username: str) -> str:
    return "".join(ch if (ch.isalnum() or ch in ("-", "_")) else "_" for ch in username)


def _cache_path(username: str) -> str:
    return f"/tmp/leetcode_profile_cache_{_safe_username(username)}.json"


def _load_cache(username: str):
    path = _cache_path(username)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    if payload.get("version") != CACHE_SCHEMA_VERSION:
        return None

    cached_at = payload.get("cached_at")
    if not isinstance(cached_at, (int, float)):
        return None
    if time.time() - cached_at > CACHE_TTL_SECONDS:
        return None

    data = payload.get("data")
    return data if isinstance(data, dict) else None


def _save_cache(username: str, data: dict):
    path = _cache_path(username)
    payload = {
        "version": CACHE_SCHEMA_VERSION,
        "cached_at": time.time(),
        "data": data,
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
    except OSError:
        # Cache write failures should not block report generation.
        pass


def _retry_delay(attempt: int, retry_after: str = None) -> float:
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            pass
    return min(2 ** attempt, 16) + random.uniform(0.0, 0.5)


def _is_retryable_graphql_error(errors) -> bool:
    for err in errors:
        msg = str(err.get("message", "")).lower()
        if ("too many requests" in msg) or ("rate limit" in msg) or ("timeout" in msg):
            return True
    return False


def graphql_request(query: str, variables: dict):
    body = json.dumps({"query": query, "variables": variables}).encode()

    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            GRAPHQL_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (leetcode-analysis)",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                parsed = json.loads(resp.read().decode())

            if parsed.get("errors"):
                if _is_retryable_graphql_error(parsed["errors"]) and attempt < MAX_RETRIES:
                    delay = _retry_delay(attempt)
                    print(f"  [!] GraphQL rate-limited, retrying in {delay:.1f}s...", file=sys.stderr)
                    time.sleep(delay)
                    continue
                print(f"  [!] GraphQL error: {parsed['errors']}", file=sys.stderr)
                return None

            return parsed.get("data")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                delay = _retry_delay(attempt, e.headers.get("Retry-After") if e.headers else None)
                print(f"  [!] HTTP {e.code}, retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"  [!] GraphQL request failed: HTTP {e.code}: {e.reason}", file=sys.stderr)
            return None
        except urllib.error.URLError as e:
            if attempt < MAX_RETRIES:
                delay = _retry_delay(attempt)
                print(f"  [!] Network error ({e}), retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"  [!] GraphQL request failed: {e}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"  [!] Failed to parse GraphQL response: {e}", file=sys.stderr)
            return None

    return None


def fetch_profile_bundle(username: str):
    query = """
query allData($username: String!, $userSlug: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum { difficulty count submissions }
      totalSubmissionNum { difficulty count submissions }
    }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
    badge { name }
  }
  userProfileUserQuestionProgressV2(userSlug: $userSlug) {
    numAcceptedQuestions { count difficulty }
    userSessionBeatsPercentage { difficulty percentage }
    totalQuestionBeatsPercentage
  }
}
""".strip()

    raw = graphql_request(query, {"username": username, "userSlug": username})
    if not raw:
        return None

    matched_user = raw.get("matchedUser")
    if not matched_user:
        print(f"  [!] User '{username}' not found or profile is private.", file=sys.stderr)
        return None

    progress = raw.get("userProfileUserQuestionProgressV2") or {}
    submit_stats = matched_user.get("submitStatsGlobal") or {}
    ac_submission = submit_stats.get("acSubmissionNum", [])
    total_submission = submit_stats.get("totalSubmissionNum", [])

    accepted_map = {
        str(item.get("difficulty", "")).upper(): int(item.get("count", 0))
        for item in progress.get("numAcceptedQuestions", [])
    }

    def fallback_count(diff_upper: str) -> int:
        for item in ac_submission:
            if str(item.get("difficulty", "")).upper() == diff_upper:
                return int(item.get("count", 0))
        return 0

    easy = accepted_map.get("EASY", fallback_count("EASY"))
    medium = accepted_map.get("MEDIUM", fallback_count("MEDIUM"))
    hard = accepted_map.get("HARD", fallback_count("HARD"))
    total = easy + medium + hard

    solved_data = {
        "easySolved": easy,
        "mediumSolved": medium,
        "hardSolved": hard,
        "solvedProblem": total,
        "totalSubmissionNum": total_submission,
        "acSubmissionNum": ac_submission,
    }

    skill_data = matched_user.get("tagProblemCounts") or {"fundamental": [], "intermediate": [], "advanced": []}

    contest_raw = raw.get("userContestRanking")
    contest_data = None
    if contest_raw:
        contest_data = {
            "contestRating": contest_raw.get("rating"),
            "contestGlobalRanking": contest_raw.get("globalRanking"),
            "contestAttend": contest_raw.get("attendedContestsCount"),
            "contestTopPercentage": contest_raw.get("topPercentage"),
            "contestBadges": contest_raw.get("badge"),
        }

    return {
        "solved": solved_data,
        "skill": skill_data,
        "progress": progress,
        "contest": contest_data,
    }


def progress_bar(filled: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "`" + "░" * width + "`"
    ratio = min(filled / total, 1.0)
    done = int(ratio * width)
    return "`" + "█" * done + "░" * (width - done) + "`"


def main():
    if len(sys.argv) < 2:
        print("Usage: leetcode_analysis.py <username>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    output_file = f"/tmp/leetcode_report_{username}.md"

    print(f"Fetching data for '{username}' from LeetCode GraphQL...", file=sys.stderr)
    bundle = _load_cache(username)
    if bundle:
        print("Using cached profile data (within 30 minutes).", file=sys.stderr)
    else:
        bundle = fetch_profile_bundle(username)
        if bundle:
            _save_cache(username, bundle)

    if not bundle:
        print("Failed to fetch essential data. Aborting.", file=sys.stderr)
        sys.exit(1)

    solved_data = bundle.get("solved")
    skill_data = bundle.get("skill")
    progress_data = bundle.get("progress")
    contest_data = bundle.get("contest")

    if not solved_data or not skill_data:
        print("Incomplete profile data returned by GraphQL. Aborting.", file=sys.stderr)
        sys.exit(1)

    print("Data fetched successfully. Generating report...", file=sys.stderr)

    md = []
    w = md.append

    easy = solved_data["easySolved"]
    medium = solved_data["mediumSolved"]
    hard = solved_data["hardSolved"]
    total = solved_data["solvedProblem"]
    easy_pct = easy / total * 100
    medium_pct = medium / total * 100
    hard_pct = hard / total * 100

    w(f"# LeetCode Progress Report — `{username}`")
    w("")
    w(f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Total Solved: **{total}**")
    w("")

    # ── 1. Difficulty Distribution ──
    w("---")
    w("")
    w("## 1. Difficulty Distribution")
    w("")
    w("| Difficulty | Solved | Percentage | Pool | Progress |")
    w("|:----------:|-------:|-----------:|-----:|:---------|")
    w(f"| Easy | {easy} | {easy_pct:.1f}% | {LEETCODE_TOTAL['EASY']} | {progress_bar(easy, total)} |")
    w(f"| Medium | {medium} | {medium_pct:.1f}% | {LEETCODE_TOTAL['MEDIUM']} | {progress_bar(medium, total)} |")
    w(f"| Hard | {hard} | {hard_pct:.1f}% | {LEETCODE_TOTAL['HARD']} | {progress_bar(hard, total)} |")
    w("")
    w("| | Your Ratio | Ideal Ratio |")
    w("|---|---|---|")
    w(f"| Distribution | Easy {easy_pct:.0f}% / Medium {medium_pct:.0f}% / Hard {hard_pct:.0f}% | Easy 20% / Medium 60% / Hard 20% |")
    w("")

    issues = []
    if hard_pct < 12:
        issues.append("Hard 題目佔比偏低，建議增加 Hard 題量")
    if easy_pct > 35:
        issues.append("Easy 題目佔比偏高，建議多練 Medium / Hard")
    if issues:
        w("> **Observations:**")
        for iss in issues:
            w(f"> - {iss}")
        w("")

    # ── 2. Topic Coverage ──
    w("---")
    w("")
    w("## 2. Topic Coverage Analysis")
    w("")

    all_skills = {}
    for level in ("fundamental", "intermediate", "advanced"):
        for item in skill_data.get(level, []):
            all_skills[item["tagName"]] = item["problemsSolved"]

    strong, adequate, weak, missing = [], [], [], []
    for topic in CORE_INTERVIEW_TOPICS:
        count = all_skills.get(topic, 0)
        benchmark = TOPIC_BENCHMARKS.get(topic, 10)
        ratio = count / benchmark if benchmark > 0 else 0
        entry = (topic, count, benchmark, ratio)
        if ratio >= 1.5:
            strong.append(entry)
        elif ratio >= 1.0:
            adequate.append(entry)
        elif count > 0:
            weak.append(entry)
        else:
            missing.append(entry)

    strong.sort(key=lambda x: -x[3])
    weak.sort(key=lambda x: x[3])

    w(f"### Strong Topics ({len(strong)})")
    w("")
    w("| Topic | Solved | Benchmark | Rating |")
    w("|:------|-------:|----------:|:------:|")
    for topic, count, bench, ratio in strong:
        w(f"| {topic} | {count} | {bench} | ★★★ |")
    w("")

    w(f"### Adequate Topics ({len(adequate)})")
    w("")
    w("| Topic | Solved | Benchmark | Rating |")
    w("|:------|-------:|----------:|:------:|")
    for topic, count, bench, ratio in adequate:
        w(f"| {topic} | {count} | {bench} | ★★☆ |")
    w("")

    if weak:
        w(f"### Weak Topics — Need More Practice ({len(weak)})")
        w("")
        w("| Topic | Solved | Benchmark | Progress |")
        w("|:------|-------:|----------:|---------:|")
        for topic, count, bench, ratio in weak:
            pct = ratio * 100
            w(f"| {topic} | {count} | {bench} | {pct:.0f}% |")
        w("")

    if missing:
        w(f"### Missing Topics ({len(missing)})")
        w("")
        for topic, count, bench, ratio in missing:
            w(f"- **{topic}** — 0 solved (benchmark: {bench})")
        w("")

    # ── 3. Performance Percentile & Accept Rate ──
    w("---")
    w("")
    w("## 3. Performance Percentile & Accept Rate")
    w("")

    if isinstance(progress_data, dict):
        beats = progress_data.get("userSessionBeatsPercentage", [])
        # Backward-compatible path for older third-party API shape.
        if not beats:
            naq = progress_data.get("numAcceptedQuestions", {})
            if isinstance(naq, dict):
                beats = naq.get("userSessionBeatsPercentage", [])
        if beats:
            w("### Beats Percentage")
            w("")
            w("> 你的表現超過了多少百分比的 LeetCode 使用者")
            w("")
            w("| Difficulty | Beats | Visual |")
            w("|:-----------|------:|:-------|")
            for b in beats:
                diff = b["difficulty"]
                pct = b["percentage"]
                w(f"| {diff} | {pct:.1f}% | {progress_bar(int(pct), 100)} |")
            w("")

    sub_total = solved_data.get("totalSubmissionNum", [])
    ac_sub = solved_data.get("acSubmissionNum", [])
    if sub_total and ac_sub:
        sub_map = {s["difficulty"]: s["submissions"] for s in sub_total}
        ac_map = {s["difficulty"]: s["submissions"] for s in ac_sub}

        w("### Accept Rate")
        w("")
        w("> 提交次數中被 Accept 的比例")
        w("")
        w("| Difficulty | Submissions | Accepted | Accept Rate |")
        w("|:-----------|------------:|---------:|------------:|")
        for diff in ("Easy", "Medium", "Hard", "All"):
            subs = sub_map.get(diff, 0)
            acs = ac_map.get(diff, 0)
            rate = (acs / subs * 100) if subs > 0 else 0
            label = f"**{diff}**" if diff == "All" else diff
            w(f"| {label} | {subs} | {acs} | {rate:.1f}% |")
        w("")

    # ── 4. Contest Performance ──
    if contest_data:
        w("---")
        w("")
        w("## 4. Contest Performance")
        w("")
        rating = contest_data.get("contestRating")
        ranking = contest_data.get("contestGlobalRanking")
        attended = contest_data.get("contestAttend")
        top_pct = contest_data.get("contestTopPercentage")
        badge = contest_data.get("contestBadges")

        w("| Metric | Value |")
        w("|:-------|------:|")
        if rating:
            w(f"| Rating | {rating:.0f} |")
        if ranking:
            w(f"| Global Rank | #{ranking} |")
        if top_pct:
            w(f"| Top | {top_pct:.1f}% |")
        if attended:
            w(f"| Contests Attended | {attended} |")
        if badge and badge.get("name"):
            w(f"| Badge | {badge['name']} |")
        w("")

    # ── 5. Weak Areas & Recommendations ──
    w("---")
    w("")
    w("## 5. Weak Areas & Recommended Problems")
    w("")

    priority_weak = list(weak[:8])
    if hard_pct < 12:
        priority_weak.append(("Hard General", hard, 0, 0))

    if not priority_weak:
        w("> No significant weak areas found! You're well-rounded.")
        w("")
    else:
        for topic, count, bench, ratio in priority_weak:
            w(f"### {topic} (solved: {count})")
            w("")
            recs = RECOMMENDED_PROBLEMS.get(topic, [])
            if recs:
                diff_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
                w("| # | Problem | Difficulty |")
                w("|--:|:--------|:----------:|")
                for pid, name, diff in recs:
                    icon = diff_icon.get(diff, "")
                    w(f"| {pid} | [{name}](https://leetcode.com/problems/{name.lower().replace(' ', '-')}) | {icon} {diff} |")
            else:
                w(f"- Search LeetCode for tag: **{topic}**")
            w("")

    # ── 6. Interview Readiness ──
    w("---")
    w("")
    w("## 6. Interview Readiness Assessment")
    w("")

    score = 0
    max_score = 100
    score_details = []

    if total >= 500:
        pts = 20
    elif total >= 300:
        pts = 15
    elif total >= 150:
        pts = 10
    else:
        pts = 5
    score += pts
    score_details.append(("Total Solved", pts, 20))

    pts = 0
    if 15 <= easy_pct <= 35:
        pts += 7
    elif easy_pct < 15:
        pts += 5
    else:
        pts += 3
    if 50 <= medium_pct <= 70:
        pts += 7
    elif medium_pct > 40:
        pts += 5
    else:
        pts += 3
    if hard_pct >= 15:
        pts += 6
    elif hard_pct >= 8:
        pts += 4
    else:
        pts += 2
    score += pts
    score_details.append(("Difficulty Balance", pts, 20))

    covered = len(strong) + len(adequate)
    total_core = len(CORE_INTERVIEW_TOPICS)
    breadth_ratio = covered / total_core
    pts = int(breadth_ratio * 25)
    score += pts
    score_details.append(("Topic Breadth", pts, 25))

    deep_count = sum(1 for t, c, b, r in strong if r >= 2.0)
    pts = min(deep_count * 2, 20)
    score += pts
    score_details.append(("Topic Depth", pts, 20))

    if hard >= 80:
        pts = 15
    elif hard >= 50:
        pts = 10
    elif hard >= 30:
        pts = 7
    elif hard >= 15:
        pts = 4
    else:
        pts = 2
    score += pts
    score_details.append(("Hard Problem Count", pts, 15))

    w("| Category | Score | Max |")
    w("|:---------|------:|----:|")
    for cat, s, m in score_details:
        w(f"| {cat} | {s} | {m} |")
    w(f"| **TOTAL** | **{score}** | **{max_score}** |")
    w("")
    w(f"**Overall: {score}/100** {progress_bar(score, 100, 30)}")
    w("")

    if score >= 85:
        level = "Interview Ready"
        desc = "你的準備非常充分，可以自信地面對大多數技術面試。"
    elif score >= 70:
        level = "Advanced"
        desc = "基礎扎實，大部分主題都有涵蓋。加強 Hard 題和少數弱項即可。"
    elif score >= 55:
        level = "Intermediate"
        desc = "有一定實力，但仍有明顯的知識缺口需要補強。"
    elif score >= 35:
        level = "Foundation"
        desc = "已建立基礎，但需要更多練習和主題覆蓋。"
    else:
        level = "Beginner"
        desc = "剛開始刷題，建議從基礎主題和 Easy 題開始。"

    w(f"> **Level: {level}**")
    w("> ")
    w(f"> {desc}")
    w("")

    # ── 7. Action Plan ──
    w("---")
    w("")
    w("## 7. Prioritized Action Plan")
    w("")

    action_num = 1
    if hard_pct < 12:
        w(f"{action_num}. **增加 Hard 題量** — 目前 {hard} 題 ({hard_pct:.1f}%)，建議至少達到 80 題以上。專注 DP、Graph、Tree 的 Hard 題。")
        action_num += 1

    for topic, count, bench, ratio in weak[:5]:
        w(f"{action_num}. **加強 {topic}** — 目前 {count} 題，建議至少做到 {bench} 題。")
        action_num += 1

    if action_num == 1:
        w("1. 持續保持，挑戰更多 Hard 題和新主題！")

    w("")
    w("---")
    w("*Report generated by leetcode_analysis.py*")
    w("")

    report = "\n".join(md)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(output_file)


if __name__ == "__main__":
    main()

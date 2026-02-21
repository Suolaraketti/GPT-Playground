"""
Reddit crawler for demand generation and lead generation threads.

Searches targeted subreddits for relevant discussions and saves results to CSV.

Usage:
    python src/reddit_crawler.py
    python src/reddit_crawler.py --limit 50 --output results/my_run.csv
"""

import argparse
import csv
import os
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Subreddits most likely to contain demand gen / lead gen discussions
TARGET_SUBREDDITS = [
    "marketing",
    "digital_marketing",
    "b2bmarketing",
    "sales",
    "salesforce",
    "hubspot",
    "startups",
    "Entrepreneur",
    "SEO",
    "PPC",
    "content_marketing",
    "leadgeneration",
    "demandgeneration",
]

# Keywords to match against post title + selftext
KEYWORDS = [
    "demand generation",
    "demand gen",
    "lead generation",
    "lead gen",
    "top of funnel",
    "tofu",
    "MQL",
    "marketing qualified lead",
    "SQL",
    "sales qualified lead",
    "pipeline generation",
    "inbound marketing",
    "outbound marketing",
    "account based marketing",
    "ABM",
    "B2B marketing",
    "content syndication",
    "paid demand",
    "intent data",
    "lead nurturing",
    "drip campaign",
    "marketing funnel",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RedditThread:
    subreddit: str
    post_id: str
    title: str
    author: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: str
    url: str
    permalink: str
    matched_keywords: str
    selftext_preview: str


# ---------------------------------------------------------------------------
# Crawler
# ---------------------------------------------------------------------------

def build_reddit_client() -> praw.Reddit:
    """Create an authenticated Reddit client from environment variables."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "GPT-Playground/1.0")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "Missing Reddit API credentials. "
            "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your .env file. "
            "See README.md for setup instructions."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        # Read-only mode — no password needed
    )


def find_matching_keywords(text: str) -> list[str]:
    """Return all keywords found in the given text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw.lower() in text_lower]


def crawl_subreddit(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int,
    sort: str = "hot",
) -> list[RedditThread]:
    """Crawl a single subreddit and return threads matching our keywords."""
    results: list[RedditThread] = []

    try:
        sub = reddit.subreddit(subreddit_name)
        posts = {
            "hot": sub.hot,
            "new": sub.new,
            "top": lambda limit: sub.top("month", limit=limit),
            "rising": sub.rising,
        }.get(sort, sub.hot)

        for post in posts(limit=limit):
            combined_text = f"{post.title} {post.selftext}"
            matched = find_matching_keywords(combined_text)

            if not matched:
                continue

            created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            preview = post.selftext[:300].replace("\n", " ").strip()
            if len(post.selftext) > 300:
                preview += "..."

            results.append(RedditThread(
                subreddit=subreddit_name,
                post_id=post.id,
                title=post.title,
                author=str(post.author) if post.author else "[deleted]",
                score=post.score,
                upvote_ratio=post.upvote_ratio,
                num_comments=post.num_comments,
                created_utc=created.strftime("%Y-%m-%d %H:%M UTC"),
                url=post.url,
                permalink=f"https://reddit.com{post.permalink}",
                matched_keywords=", ".join(matched),
                selftext_preview=preview,
            ))

    except Exception as exc:
        print(f"  [warn] r/{subreddit_name}: {exc}")

    return results


def crawl_all(
    reddit: praw.Reddit,
    subreddits: list[str],
    limit: int,
    sort: str,
    delay: float = 1.0,
) -> list[RedditThread]:
    """Crawl all subreddits with a polite delay between requests."""
    all_results: list[RedditThread] = []
    seen_ids: set[str] = set()

    for i, name in enumerate(subreddits, 1):
        print(f"[{i}/{len(subreddits)}] Crawling r/{name} ({sort}, limit={limit})...")
        threads = crawl_subreddit(reddit, name, limit, sort)

        # Deduplicate cross-posted content
        new_threads = [t for t in threads if t.post_id not in seen_ids]
        seen_ids.update(t.post_id for t in new_threads)
        all_results.extend(new_threads)

        print(f"         Found {len(new_threads)} matching thread(s) (total: {len(all_results)})")

        if i < len(subreddits):
            time.sleep(delay)

    return all_results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_to_csv(threads: list[RedditThread], output_path: Path) -> None:
    """Write threads to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    column_names = [f.name for f in fields(RedditThread)]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        writer.writeheader()
        for thread in threads:
            writer.writerow({f.name: getattr(thread, f.name) for f in fields(thread)})

    print(f"\nSaved {len(threads)} threads to {output_path}")


def print_summary(threads: list[RedditThread]) -> None:
    """Print a brief summary to the terminal."""
    if not threads:
        print("\nNo matching threads found.")
        return

    print(f"\n{'='*70}")
    print(f"  Found {len(threads)} relevant thread(s)")
    print(f"{'='*70}")

    # Sort by score descending for the preview
    top = sorted(threads, key=lambda t: t.score, reverse=True)[:10]
    for i, t in enumerate(top, 1):
        print(f"\n{i}. [{t.subreddit}] {t.title}")
        print(f"   Score: {t.score}  |  Comments: {t.num_comments}  |  {t.created_utc}")
        print(f"   Keywords: {t.matched_keywords}")
        print(f"   {t.permalink}")

    if len(threads) > 10:
        print(f"\n   ... and {len(threads) - 10} more — see the CSV for all results.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crawl Reddit for demand generation and lead generation threads."
    )
    parser.add_argument(
        "--limit", type=int, default=25,
        help="Number of posts to fetch per subreddit (default: 25)",
    )
    parser.add_argument(
        "--sort", choices=["hot", "new", "top", "rising"], default="hot",
        help="Sort method for posts (default: hot)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Path to save CSV output. Defaults to results/reddit_<timestamp>.csv",
    )
    parser.add_argument(
        "--subreddits", nargs="+", default=None,
        help="Override the list of subreddits to crawl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output) if args.output else Path(f"results/reddit_{timestamp}.csv")
    subreddits = args.subreddits or TARGET_SUBREDDITS

    print("Reddit Demand Gen / Lead Gen Crawler")
    print(f"Subreddits : {len(subreddits)}")
    print(f"Posts/sub  : {args.limit}")
    print(f"Sort by    : {args.sort}")
    print(f"Output     : {output_path}")
    print()

    reddit = build_reddit_client()
    threads = crawl_all(reddit, subreddits, args.limit, args.sort)

    print_summary(threads)

    if threads:
        save_to_csv(threads, output_path)


if __name__ == "__main__":
    main()

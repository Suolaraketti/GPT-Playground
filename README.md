# GPT-Playground

A collection of scripts for experimenting with AI APIs and data collection tools.

---

## Reddit Crawler — Demand Gen & Lead Gen Threads

Searches Reddit for discussions about demand generation and lead generation campaigns across 13 marketing-focused subreddits. Results are saved to a CSV file.

### What it crawls

**Subreddits:** r/marketing, r/digital_marketing, r/b2bmarketing, r/sales, r/salesforce, r/hubspot, r/startups, r/Entrepreneur, r/SEO, r/PPC, r/content_marketing, r/leadgeneration, r/demandgeneration

**Keywords matched:** demand generation, demand gen, lead generation, lead gen, MQL, SQL, ABM, account based marketing, top of funnel, pipeline generation, intent data, and more.

---

### Setup

#### 1. Get Reddit API credentials (free, takes 2 minutes)

1. Log in to Reddit and go to **https://www.reddit.com/prefs/apps**
2. Scroll down and click **"create another app..."**
3. Fill in the form:
   - **Name:** anything (e.g. `gpt-playground`)
   - **Type:** select **script**
   - **Redirect URI:** `http://localhost:8080`
4. Click **Create app**
5. You'll see your app listed. Note:
   - **Client ID** — the string under your app name (looks like `abc123xyz`)
   - **Client Secret** — the string next to "secret"

#### 2. Install dependencies

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install packages
pip install -r requirements.txt
```

#### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
REDDIT_CLIENT_ID=abc123xyz
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=GPT-Playground/1.0 by u/your_reddit_username
```

---

### Run it

```bash
# Default: crawl all subreddits, 25 posts each, sorted by hot
python src/reddit_crawler.py

# Fetch more posts per subreddit
python src/reddit_crawler.py --limit 50

# Sort by newest posts instead of hot
python src/reddit_crawler.py --sort new

# Sort by top posts this month
python src/reddit_crawler.py --sort top

# Only crawl specific subreddits
python src/reddit_crawler.py --subreddits marketing b2bmarketing sales

# Custom output file
python src/reddit_crawler.py --output results/my_run.csv

# Combine options
python src/reddit_crawler.py --limit 100 --sort top --output results/top100.csv
```

Results are saved to `results/reddit_<timestamp>.csv` by default. The `results/` folder is git-ignored so your data stays local.

---

### Output columns

| Column | Description |
|---|---|
| `subreddit` | Which subreddit the post is from |
| `post_id` | Reddit's unique post ID |
| `title` | Post title |
| `author` | Reddit username of the poster |
| `score` | Net upvotes |
| `upvote_ratio` | Ratio of upvotes to total votes |
| `num_comments` | Number of comments |
| `created_utc` | Post date/time (UTC) |
| `url` | Link the post points to |
| `permalink` | Direct link to the Reddit thread |
| `matched_keywords` | Which keywords triggered the match |
| `selftext_preview` | First 300 characters of the post body |

---

### Troubleshooting

**`EnvironmentError: Missing Reddit API credentials`**
Make sure your `.env` file exists and has `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` filled in.

**`prawcore.exceptions.ResponseException: received 401 HTTP response`**
Your credentials are wrong. Double-check the client ID and secret from the Reddit app page.

**A subreddit shows a warning and no results**
The subreddit may be private, banned, or have very few posts. The crawler skips it and continues.

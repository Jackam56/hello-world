"""Feed sources and filter settings for the daily news digest."""

# Each entry: (source name, feed URL). Grouped by section, in display order.
FEEDS = {
    "World": [
        ("ABC News International", "https://feeds.abcnews.com/abcnews/internationalheadlines"),
        ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ],
    "National (U.S.)": [
        ("ABC News U.S.", "https://feeds.abcnews.com/abcnews/usheadlines"),
        ("NPR National", "https://feeds.npr.org/1003/rss.xml"),
    ],
    "Michigan": [
        ("Bridge Michigan", "https://www.bridgemi.com/feed"),
        ("MLive Michigan News", "https://www.mlive.com/arc/outboundfeeds/rss/category/news/?outputType=xml"),
    ],
    "Flint / Swartz Creek": [
        ("MLive Flint", "https://www.mlive.com/arc/outboundfeeds/rss/category/flint-news/?outputType=xml"),
        ("Flint Beat", "https://flintbeat.com/feed/"),
    ],
}

# Only include items published within this many hours of when the digest runs.
MAX_AGE_HOURS = 30

# Max stories to show per section.
MAX_ITEMS_PER_SECTION = 8

# Any headline/summary containing one of these (case-insensitive) is treated
# as "about Trump" and gets held to the higher bar below.
TRUMP_KEYWORDS = ["trump"]

# A Trump-related story is only included if it ALSO matches one of these,
# i.e. it's a major/historic event rather than routine coverage.
TRUMP_SEVERITY_KEYWORDS = [
    "assassinat",
    "shot", "shooting", "gunman", "gunshot",
    "war", "invade", "invasion", "martial law", "nuclear",
    "coup",
    "resign",
    "impeach",
    "indict", "convicted", "guilty verdict", "sentenced",
    "dies", "dead", "death", "hospitalized", "hospitalised",
    "national emergency", "constitutional crisis",
]

EMAIL_SUBJECT_PREFIX = "Daily News Digest"

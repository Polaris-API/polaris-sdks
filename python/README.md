# polaris-news

Official Python SDK for [The Polaris Report](https://thepolarisreport.com) API.

## Installation

```bash
pip install polaris-news
```

## Quick Start

### Authenticate via CLI

```bash
polaris login    # opens GitHub in your browser — API key saved automatically
polaris whoami   # check your auth status
polaris logout   # remove saved credentials
```

### Use the client

```python
from polaris_news import PolarisClient

client = PolarisClient()  # auto-reads saved credentials
feed = client.feed(category="technology", limit=10)
for brief in feed.briefs:
    print(brief.headline)
```

You can also pass a key explicitly or set the `POLARIS_API_KEY` environment variable.

## Methods

| Method | Description |
|--------|-------------|
| `feed(category?, limit?, page?, per_page?, min_confidence?)` | Get the news feed |
| `brief(brief_id, include_full_text?)` | Get a single brief by ID |
| `search(query, category?, page?, per_page?, sort?, min_confidence?, from_date?, to_date?, entity?, sentiment?)` | Search briefs |
| `generate(topic, category?)` | Generate a brief on a topic |
| `entities(q?, type?, limit?)` | List entities |
| `entity_briefs(name, role?, limit?, offset?)` | Get briefs for an entity |
| `trending_entities(limit?)` | Get trending entities |
| `similar(brief_id, limit?)` | Get similar briefs |
| `clusters(period?, limit?)` | Get brief clusters |
| `data(entity?, type?, limit?)` | Get structured data points |
| `agent_feed(category?, tags?, limit?, min_confidence?)` | Get agent-optimized feed |
| `compare_sources(brief_id)` | Compare sources for a brief |
| `trending(period?, limit?)` | Get trending briefs |
| `stream(categories?)` | Stream briefs via SSE (generator) |

## Error Handling

```python
from polaris_news import PolarisClient, AuthenticationError, RateLimitError, NotFoundError

client = PolarisClient()

try:
    brief = client.brief("abc123")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Brief not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
```

## Streaming

```python
client = PolarisClient()

for brief in client.stream(categories="technology,science"):
    print(f"[{brief.category}] {brief.headline}")
```

## Documentation

Full API documentation: https://thepolarisreport.com/docs

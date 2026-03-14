# Polaris SDKs

Official Python and TypeScript SDKs for [The Polaris Report](https://thepolarisreport.com) API.

## SDKs

| Language | Package | Install |
|----------|---------|---------|
| Python | [`polaris-news`](./python/) | `pip install polaris-news` |
| TypeScript | [`polaris-news-api`](./typescript/) | `npm install polaris-news-api` |

## Quick Start

### Authenticate via CLI

```bash
pip install polaris-news   # or: npm install polaris-news-api
polaris login              # opens GitHub — API key saved to ~/.polaris/credentials
```

### Python

```python
from polaris_news import PolarisClient

client = PolarisClient()  # auto-reads saved credentials
feed = client.feed(category="technology", limit=10)
for brief in feed.briefs:
    print(brief.headline)
```

### TypeScript

```typescript
import { PolarisClient } from "polaris-news-api";

const client = new PolarisClient();  // auto-reads saved credentials
const feed = await client.feed({ category: "technology", limit: 10 });
feed.briefs.forEach((brief) => console.log(brief.headline));
```

### API Key Resolution

Both SDKs resolve the API key in this order:
1. Explicit parameter (`api_key=` / `apiKey:`)
2. `POLARIS_API_KEY` environment variable
3. `~/.polaris/credentials` file (written by `polaris login`)

## Documentation

Full API documentation: https://thepolarisreport.com/docs

## License

MIT

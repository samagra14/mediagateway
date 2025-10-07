# MediaRouter Examples

Practical examples for using MediaRouter.

## Quick Examples

### Generate Your First Video

1. Start the application:
```bash
./setup.sh
```

2. Open http://localhost:3000

3. Go to Settings → Add API Key (e.g., OpenAI)

4. Go to Playground and try:
```
Prompt: "A majestic eagle soaring over snow-capped mountains at sunset"
Model: sora-2
Duration: 5 seconds
Aspect Ratio: 16:9
```

## API Examples

### Using cURL

**Generate Video:**
```bash
curl -X POST http://localhost:3001/v1/video/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sora-2",
    "prompt": "A serene sunset over mountains",
    "duration": 5,
    "aspect_ratio": "16:9",
    "seed": 42
  }'
```

**Check Status:**
```bash
curl http://localhost:3001/v1/video/generations/gen_abc123
```

**List Generations:**
```bash
curl http://localhost:3001/v1/video/generations?limit=10
```

### Using Python

```python
import requests
import time

API_BASE = "http://localhost:3001/v1"

# Generate video
response = requests.post(
    f"{API_BASE}/video/generations",
    json={
        "model": "sora-2",
        "prompt": "A peaceful ocean wave at sunrise",
        "duration": 5,
        "aspect_ratio": "16:9"
    }
)

generation = response.json()
generation_id = generation["id"]
print(f"Started generation: {generation_id}")

# Poll for completion
while True:
    status = requests.get(
        f"{API_BASE}/video/generations/{generation_id}"
    ).json()

    print(f"Status: {status['status']}")

    if status["status"] == "completed":
        print(f"Video URL: {status['video']['url']}")
        break
    elif status["status"] == "failed":
        print(f"Error: {status.get('error')}")
        break

    time.sleep(5)
```

### Using JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const API_BASE = 'http://localhost:3001/v1';

async function generateVideo() {
  // Create generation
  const response = await fetch(`${API_BASE}/video/generations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'sora-2',
      prompt: 'A tranquil forest stream with sunlight filtering through trees',
      duration: 5,
      aspect_ratio: '16:9'
    })
  });

  const generation = await response.json();
  const generationId = generation.id;
  console.log(`Started generation: ${generationId}`);

  // Poll for status
  while (true) {
    const statusRes = await fetch(
      `${API_BASE}/video/generations/${generationId}`
    );
    const status = await statusRes.json();

    console.log(`Status: ${status.status}`);

    if (status.status === 'completed') {
      console.log(`Video URL: ${status.video.url}`);
      break;
    } else if (status.status === 'failed') {
      console.log(`Error: ${status.error}`);
      break;
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

generateVideo();
```

## Prompt Examples

### Landscape Videos

```
"A serene sunset over snow-capped mountains with birds flying"

"A peaceful ocean beach at golden hour with gentle waves"

"A misty forest with sunlight filtering through tall trees"

"A desert landscape at dusk with cacti silhouettes"
```

### Abstract/Artistic

```
"Colorful paint splashing in slow motion against white background"

"Geometric shapes morphing and rotating in space with neon colors"

"Ink dispersing in water creating abstract patterns"

"Particle explosion with rainbow colors in dark space"
```

### Urban Scenes

```
"A busy Tokyo street at night with neon signs reflecting on wet pavement"

"Time-lapse of New York City traffic from above at sunset"

"A quiet European cobblestone street in morning light"

"A modern city skyline at golden hour with clouds moving"
```

### Nature

```
"A waterfall cascading into a crystal clear pool surrounded by lush vegetation"

"Cherry blossoms falling in slow motion in a Japanese garden"

"Northern lights dancing over a frozen lake at night"

"A field of sunflowers swaying in the wind under blue sky"
```

## Integration Examples

### With Express.js Backend

```javascript
const express = require('express');
const fetch = require('node-fetch');

const app = express();
app.use(express.json());

app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, model = 'sora-2' } = req.body;

    const response = await fetch('http://localhost:3001/v1/video/generations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        duration: 5,
        aspect_ratio: '16:9'
      })
    });

    const generation = await response.json();
    res.json(generation);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(4000, () => {
  console.log('Server running on port 4000');
});
```

### With Flask Backend

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_BASE = "http://localhost:3001/v1"

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        model = data.get('model', 'sora-2')

        response = requests.post(
            f"{API_BASE}/video/generations",
            json={
                "model": model,
                "prompt": prompt,
                "duration": 5,
                "aspect_ratio": "16:9"
            }
        )

        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=4000)
```

### With Next.js

```typescript
// app/api/generate/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { prompt, model = 'sora-2' } = await request.json();

    const response = await fetch('http://localhost:3001/v1/video/generations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        duration: 5,
        aspect_ratio: '16:9'
      })
    });

    const generation = await response.json();
    return NextResponse.json(generation);
  } catch (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
```

## Best Practices

### Prompt Engineering

1. **Be Specific**: Include details about lighting, time of day, mood
2. **Use Descriptive Language**: Rich adjectives help guide generation
3. **Consider Motion**: Describe what movement should occur
4. **Set the Scene**: Include context and environment details

**Good:**
```
"A majestic golden eagle soaring through a canyon at sunset,
dramatic lighting, slow motion, cinematic"
```

**Better:**
```
"Close-up of a golden eagle with spread wings gliding through
a red sandstone canyon at golden hour, warm sunlight illuminating
feathers, slow graceful motion, cinematic depth of field"
```

### Error Handling

```python
import requests
from typing import Optional

def generate_video_with_retry(
    prompt: str,
    model: str = "sora-2",
    max_retries: int = 3
) -> Optional[dict]:
    """Generate video with automatic retry on failure."""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:3001/v1/video/generations",
                json={"model": model, "prompt": prompt},
                timeout=300
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                # Invalid request, don't retry
                raise
            print(f"HTTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise

    return None
```

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Rate limit decorator."""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def generate_video(prompt: str):
    # Your generation code here
    pass
```

## Advanced Use Cases

### Batch Generation

```python
import asyncio
import aiohttp

async def generate_batch(prompts: list[str]):
    """Generate multiple videos concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for prompt in prompts:
            task = session.post(
                "http://localhost:3001/v1/video/generations",
                json={"model": "sora-2", "prompt": prompt}
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Usage
prompts = [
    "A sunset over mountains",
    "A forest stream",
    "An ocean wave"
]
results = asyncio.run(generate_batch(prompts))
```

### Webhook Integration

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/generation-complete', methods=['POST'])
def generation_complete():
    """Receive webhook when generation completes."""
    data = request.json
    generation_id = data['id']
    video_url = data['video']['url']

    # Process completed video
    print(f"Generation {generation_id} completed: {video_url}")

    # Your custom logic here
    # - Send notification
    # - Update database
    # - Post to social media
    # etc.

    return {'status': 'received'}, 200
```

## Troubleshooting Examples

### Check Provider Status

```bash
# List all providers and their status
curl http://localhost:3001/v1/providers | jq

# Validate specific API key
curl -X POST http://localhost:3001/v1/keys/1/validate
```

### Monitor Usage

```bash
# Get usage statistics
curl http://localhost:3001/v1/usage/stats | jq

# Filter by provider
curl "http://localhost:3001/v1/video/generations?provider=openai&limit=5" | jq
```

### Debug Failed Generations

```python
import requests

# Get failed generations
response = requests.get(
    "http://localhost:3001/v1/video/generations",
    params={"status": "failed", "limit": 10}
)

for gen in response.json():
    print(f"ID: {gen['id']}")
    print(f"Prompt: {gen['prompt']}")
    print(f"Error: {gen.get('error', 'Unknown')}")
    print("---")
```

## More Examples

For more examples and use cases, check out:
- [API Documentation](http://localhost:3001/docs)
- [GitHub Discussions](https://github.com/yourusername/mediarouter/discussions)
- [Community Examples](https://github.com/yourusername/mediarouter/tree/main/examples)

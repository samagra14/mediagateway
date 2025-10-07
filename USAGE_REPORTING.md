# Usage & Cost Reporting - Complete Implementation ✅

## Overview

MediaRouter now includes comprehensive usage tracking and cost reporting to help you monitor spending across all video generation providers.

## Features Added

### 1. **Cost Calculator Service** (`backend/src/services/cost_calculator.py`)

Centralized cost calculation for all providers:

- **Sora 2**: $0.10/second
- **Runway Gen-3**: $0.05/second (estimated)
- **Runway Gen-4**: $0.075/second (estimated)
- **Kling 1.5**: $0.04/second (estimated)
- **Kling 1.0**: $0.03/second (estimated)

Features:
- Resolution-based cost multipliers
- Per-second pricing
- Cost estimation before generation
- Support for all providers

### 2. **New API Endpoints**

#### **POST /v1/usage/estimate**
Estimate cost before generating a video.

**Request:**
```json
{
  "model": "sora-2",
  "prompt": "dummy",
  "duration": 5,
  "aspect_ratio": "16:9"
}
```

**Response:**
```json
{
  "model": "sora-2",
  "provider": "openai",
  "duration": 5,
  "aspect_ratio": "16:9",
  "estimated_cost": 0.5,
  "per_second_rate": 0.1,
  "resolution": "1280x720",
  "breakdown": {
    "base": 0.0,
    "duration_cost": 0.5
  }
}
```

#### **GET /v1/usage/detailed**
Get detailed usage statistics with date filtering.

**Query Parameters:**
- `start_date`: ISO format (YYYY-MM-DD)
- `end_date`: ISO format (YYYY-MM-DD)
- `provider`: Filter by provider

**Response:**
```json
{
  "summary": {
    "total_generations": 25,
    "total_cost": 12.50,
    "total_video_duration": 125.0,
    "total_processing_time": 1250.0,
    "average_cost_per_generation": 0.5
  },
  "daily": [
    {
      "date": "2025-10-07",
      "count": 5,
      "cost": 2.50,
      "duration": 25.0,
      "success": 5,
      "failed": 0
    }
  ],
  "by_provider": [
    {
      "provider": "openai",
      "count": 15,
      "cost": 7.50,
      "duration": 75.0,
      "avg_cost_per_second": 0.1
    }
  ],
  "date_range": {
    "start": "2025-10-01",
    "end": "2025-10-07"
  }
}
```

#### **GET /v1/usage/pricing**
Get current pricing for all providers and models.

**Response:**
```json
{
  "pricing": [
    {
      "provider": "openai",
      "model": "sora-2",
      "per_second": 0.1,
      "base_cost": 0.0,
      "currency": "USD",
      "examples": {
        "5_seconds": 0.5,
        "10_seconds": 1.0,
        "20_seconds": 2.0
      }
    }
  ],
  "last_updated": "2025-10-07",
  "note": "Prices are estimates. Actual costs may vary."
}
```

### 3. **Usage Dashboard** (`frontend/src/pages/Usage.tsx`)

New page accessible at `/usage` showing:

**Summary Cards:**
- Total Cost (with average per video)
- Total Generations
- Total Video Duration
- Total Processing Time

**Cost by Provider:**
- Breakdown of spending per provider
- Number of videos generated
- Total duration
- Average cost per second
- Visual progress bar

**Daily Usage:**
- Day-by-day breakdown (last 7 days)
- Videos generated
- Success/failure counts
- Daily costs and duration

**Current Pricing:**
- Cost per second for each model
- Example costs for 5s, 10s, 20s videos
- Easy comparison across providers

### 4. **Cost Estimator in Playground**

Real-time cost estimation in the Playground:
- Updates automatically when you change:
  - Model selection
  - Duration
  - Aspect ratio
- Shows estimated cost before you generate
- Helps you make informed decisions

**Example:**
```
Estimated Cost: $0.5000
Based on 5s video at 16:9 resolution
```

### 5. **Cost Display in Gallery**

Each video card now shows:
- Cost of generation
- Time taken to generate
- Visible at a glance

### 6. **Automatic Cost Calculation**

Background task now:
- Extracts video metadata (duration, resolution)
- Calculates actual cost using the cost calculator
- Stores cost in database
- Available in all API responses

## Usage Examples

### Check Current Spending

```bash
# Get detailed usage for last 30 days
curl "http://localhost:3001/v1/usage/detailed?start_date=2025-09-07&end_date=2025-10-07"
```

### Estimate Cost Before Generation

```bash
curl -X POST http://localhost:3001/v1/usage/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sora-2",
    "prompt": "A cat playing piano",
    "duration": 10,
    "aspect_ratio": "16:9"
  }'
```

### View Pricing

```bash
curl http://localhost:3001/v1/usage/pricing
```

## Database Changes

The `generations` table already had a `cost` column - now it's properly populated:

```sql
SELECT
  provider,
  model,
  COUNT(*) as count,
  SUM(cost) as total_cost,
  AVG(cost) as avg_cost
FROM generations
WHERE status = 'completed'
GROUP BY provider, model;
```

## UI Navigation

Access the Usage dashboard from the main navigation:

```
Playground → Gallery → Usage → Settings
           ↑                      ↑
```

## Cost Breakdown by Provider

| Provider | Model | Per Second | 5s | 10s | 20s |
|----------|-------|------------|-------|--------|---------|
| OpenAI | sora-2 | $0.10 | $0.50 | $1.00 | $2.00 |
| OpenAI | sora-1 | $0.10 | $0.50 | $1.00 | $2.00 |
| Runway | gen3 | $0.05 | $0.25 | $0.50 | $1.00 |
| Runway | gen4 | $0.075 | $0.38 | $0.75 | $1.50 |
| Kling | 1.5 | $0.04 | $0.20 | $0.40 | $0.80 |
| Kling | 1.0 | $0.03 | $0.15 | $0.30 | $0.60 |

**Note**: Runway and Kling prices are estimates based on their credit systems. Actual costs may vary.

## Key Metrics Tracked

1. **Cost Metrics**
   - Total spend
   - Cost per generation
   - Cost per second
   - Cost by provider
   - Cost by model
   - Daily spending trends

2. **Usage Metrics**
   - Total videos generated
   - Success rate
   - Failure rate
   - Average generation time
   - Total video duration produced
   - Total processing time

3. **Performance Metrics**
   - Generation time per video
   - Success/failure rates
   - Provider performance comparison

## Export & Reporting

### Get Data for Excel/Sheets

```bash
# Get JSON data
curl "http://localhost:3001/v1/usage/detailed?start_date=2025-10-01&end_date=2025-10-31" > usage_october.json

# Get all generations
curl "http://localhost:3001/v1/video/generations?limit=1000" > all_generations.json
```

### Generate Monthly Report

```python
import requests
import json
from datetime import datetime, timedelta

# Get last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

response = requests.get(
    f"http://localhost:3001/v1/usage/detailed",
    params={
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
)

report = response.json()

print(f"Monthly Report: {start_date.strftime('%B %Y')}")
print(f"Total Spend: ${report['summary']['total_cost']:.2f}")
print(f"Total Videos: {report['summary']['total_generations']}")
print(f"Avg Cost/Video: ${report['summary']['average_cost_per_generation']:.4f}")

for provider in report['by_provider']:
    print(f"\n{provider['provider'].upper()}:")
    print(f"  Videos: {provider['count']}")
    print(f"  Cost: ${provider['cost']:.2f}")
    print(f"  Avg $/sec: ${provider['avg_cost_per_second']:.4f}")
```

## Cost Optimization Tips

1. **Choose the Right Provider**
   - Kling is cheapest for simple videos
   - Runway mid-range with good quality
   - Sora expensive but includes audio

2. **Optimize Duration**
   - Cost scales linearly with duration
   - Generate shorter clips and stitch together
   - 2x 5s videos = same as 1x 10s video

3. **Monitor Daily Spending**
   - Check Usage dashboard regularly
   - Set informal budgets per day/week
   - Track which prompts cost most

4. **Batch Generation**
   - Generate multiple videos in one session
   - Compare costs across providers
   - Use estimates before generating

## Future Enhancements

Potential additions:

- [ ] Budget alerts (email when over $X)
- [ ] Cost forecasting based on usage trends
- [ ] Provider recommendations based on cost
- [ ] Bulk cost estimation
- [ ] CSV export for reports
- [ ] Monthly email summaries
- [ ] Cost limits per provider
- [ ] Refund tracking for failed generations

## Testing

To test the usage reporting:

```bash
# Restart backend with new code
docker compose restart backend

# Generate a few test videos
# Then check the Usage page

# Or query the API directly
curl http://localhost:3001/v1/usage/detailed
```

## API Documentation

Full API docs with examples available at:
```
http://localhost:3001/docs
```

Look for the `/v1/usage/*` endpoints.

---

**Status**: ✅ Fully Operational
**Added**: October 2025
**Version**: MediaRouter 1.1 with Usage Reporting

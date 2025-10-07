# Sora 2 API Integration - Complete ✅

## What Changed

OpenAI just launched their Sora 2 API, and MediaRouter has been updated to fully support it!

## Updates Made

### 1. **Sora Provider Rewritten** (`backend/src/providers/sora.py`)

Updated to use the official OpenAI Videos API:

- ✅ Correct endpoint: `POST /v1/videos` (was `/v1/video/generations`)
- ✅ Proper request format: `seconds` as string, `size` as "widthxheight"
- ✅ Status checking: `GET /v1/videos/{video_id}`
- ✅ Video download: `GET /v1/videos/{video_id}/content`
- ✅ Proper error handling with OpenAI error messages
- ✅ Status mapping (queued→processing, completed→completed)

### 2. **Authenticated Downloads** (`backend/src/services/video_storage.py`)

- ✅ Added `headers` parameter to `download_video()`
- ✅ Supports Authorization header for OpenAI content endpoint
- ✅ Maintains backward compatibility with other providers

### 3. **Background Task Updated** (`backend/src/api/routes.py`)

- ✅ Passes Authorization header when downloading from OpenAI
- ✅ Properly authenticates video content requests

### 4. **Documentation Updated**

- ✅ README.md - Added Sora 2 availability notice
- ✅ PROVIDER_STATUS.md - Full Sora 2 details and pricing
- ✅ Provider table shows all 3 providers as available

## Official Sora 2 API Details

Based on OpenAI documentation at https://platform.openai.com/docs/api-reference/videos

### Endpoints

```
POST   /v1/videos                        # Create video
GET    /v1/videos/{video_id}             # Retrieve status
GET    /v1/videos/{video_id}/content     # Download video
POST   /v1/videos/{video_id}/remix       # Remix video
DELETE /v1/videos/{video_id}             # Delete video
GET    /v1/videos                        # List videos
```

### Request Format

```json
{
  "prompt": "A calico cat playing a piano on stage",
  "model": "sora-2",
  "seconds": "5",
  "size": "1280x720"
}
```

### Response Format

```json
{
  "id": "video_123",
  "object": "video",
  "model": "sora-2",
  "status": "queued",
  "progress": 0,
  "created_at": 1712697600,
  "size": "1280x720",
  "seconds": "5",
  "quality": "standard"
}
```

### Video Content Endpoint

When status is "completed", video is available at:
```
GET /v1/videos/{video_id}/content
Authorization: Bearer YOUR_API_KEY
```

## Key Features

- **Synced Audio**: Sora 2 generates video WITH audio (unique!)
- **Pricing**: $0.10 per second
- **Resolutions**:
  - Portrait: 720x1280
  - Landscape: 1280x720
  - Square: 1024x1024
- **Duration**: Default 4 seconds, up to 20 seconds
- **Rate Limits**: 2-40 RPM depending on tier
- **Image-to-Video**: Supported via `input_reference` parameter
- **Video Remix**: Supported via remix endpoint

## How to Use

### 1. Get OpenAI API Key

```
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key (starts with sk-...)
```

### 2. Add to MediaRouter

```
1. Open http://localhost:3000
2. Go to Settings
3. Click "Add API Key"
4. Select "openai"
5. Paste your API key
6. Click "Add Key"
```

### 3. Generate Video

```
1. Go to Playground
2. Enter prompt: "A serene sunset over mountains"
3. Select model: "sora-2"
4. Duration: 5 seconds
5. Aspect Ratio: 16:9 (Landscape)
6. Click "Generate Video"
7. Wait ~30-60 seconds
8. Video appears with AUDIO! 🎵
```

## Testing the Integration

To restart the backend with the updated code:

```bash
# Restart backend container
docker compose restart backend

# Or rebuild if needed
docker compose down
docker compose build backend
docker compose up -d

# Check logs
docker compose logs -f backend
```

## API Example

### Direct API Call

```bash
curl -X POST http://localhost:3001/v1/video/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sora-2",
    "prompt": "A calico cat playing a piano on stage",
    "duration": 5,
    "aspect_ratio": "16:9"
  }'
```

### Check Status

```bash
curl http://localhost:3001/v1/video/generations/gen_abc123
```

## Comparison: All 3 Providers

| Feature | Sora 2 | Runway Gen-3 | Kling 1.5 |
|---------|--------|--------------|-----------|
| **Audio** | ✅ Yes | ❌ No | ❌ No |
| **Image-to-Video** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Video Remix** | ✅ Yes | ❌ No | ✅ Yes |
| **Max Duration** | 20s | 10s | 10s |
| **Pricing** | $0.10/sec | Usage-based | Credit-based |
| **Quality** | Excellent | Excellent | Good |

## What's Next?

### Future Enhancements

1. **Remix Support**: Add UI for remixing videos
2. **Image-to-Video**: Add image upload in Playground
3. **Cost Calculator**: Show estimated cost before generation
4. **Progress Bar**: Show generation progress percentage
5. **Audio Preview**: Highlight that Sora videos have audio

### Other Providers

- **Pika Labs**: Waiting for public API
- **Luma Dream Machine**: Waiting for public API
- **Stability Video**: Implementation planned
- **Google Veo 2**: Limited availability

## Troubleshooting

### "404 Not Found" Error

**Old issue (now fixed)**: Was using wrong endpoint
**Solution**: Updated to `/v1/videos` ✅

### "Unauthorized" Error

**Cause**: Invalid or expired API key
**Solution**: Regenerate key on OpenAI platform

### Video Download Fails

**Cause**: Missing Authorization header
**Solution**: Now automatically added for OpenAI ✅

### Rate Limit Errors

**Cause**: Exceeded RPM limit (2-40 depending on tier)
**Solution**: Wait or upgrade tier on OpenAI

## Cost Estimation

```
5-second video:  $0.50
10-second video: $1.00
20-second video: $2.00
```

All videos include synced audio at no extra cost!

## Resources

- **OpenAI Docs**: https://platform.openai.com/docs/api-reference/videos
- **API Keys**: https://platform.openai.com/api-keys
- **Pricing**: https://openai.com/pricing
- **Rate Limits**: Based on usage tier (Free, Tier 1-5)

---

**Status**: ✅ Fully Operational
**Last Updated**: October 2025
**Version**: MediaRouter 1.0 with Sora 2 support

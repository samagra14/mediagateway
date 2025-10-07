# Provider Status

Current status of video generation providers in MediaRouter.

## 🎉 Update: Sora 2 Now Available!

As of October 2025, **OpenAI's Sora 2 API is now publicly available**! All three major providers (Sora, Runway, and Kling) are working.

## Provider Availability

### ✅ Currently Available

All these providers have public APIs you can use right now:

#### **OpenAI Sora 2** 🔥 NEW!
- **Status**: ✅ Public API Available (Just Launched!)
- **Endpoint**: `https://api.openai.com/v1/videos`
- **Get API Key**: https://platform.openai.com/api-keys
- **Models**: `sora-2` (flagship), `sora-1`
- **Features**: Text-to-video, Image-to-video, **Synced Audio** 🎵
- **Pricing**: **$0.10 per second**
- **Resolutions**: Portrait (720x1280), Landscape (1280x720)
- **Rate Limits**: 2-40 RPM depending on tier
- **Unique Feature**: Generates video WITH synced audio!

#### **Runway Gen-3/Gen-4**
- **Status**: ✅ Public API Available
- **Endpoint**: `https://api.runwayml.com/v1`
- **Get API Key**: https://app.runwayml.com/ → Settings → API Keys
- **Models**: `runway-gen3`, `runway-gen4`
- **Features**: Text-to-video, Image-to-video
- **Pricing**: Pay-as-you-go (usage-based)

#### **Kling AI**
- **Status**: ✅ Public API Available
- **Endpoint**: `https://api.klingai.com/v1`
- **Get API Key**: https://klingai.com/ → API section
- **Models**: `kling-1.5`, `kling-1.0`
- **Features**: Text-to-video, Image-to-video, Video-to-video
- **Pricing**: Credit-based

### 📋 Planned

These providers will be added when their APIs become available:

- **Pika Labs** - API in development
- **Luma Dream Machine** - API in development
- **Haiper** - API in development
- **Stability AI Video** - API available (pending implementation)
- **Google Veo 2** - Limited availability

## How to Use Available Providers

### 1. Get API Keys

**Runway:**
```
1. Go to https://app.runwayml.com/
2. Sign up / Login
3. Navigate to Settings → API Keys
4. Create new API key
5. Copy the key
```

**Kling AI:**
```
1. Go to https://klingai.com/
2. Create an account
3. Navigate to API section
4. Generate API key
5. Copy the key
```

### 2. Add to MediaRouter

```
1. Open http://localhost:3000
2. Go to Settings
3. Click "Add API Key"
4. Select provider (runway or kling)
5. Paste your API key
6. Click "Add Key"
```

### 3. Generate Videos

```
1. Go to Playground
2. Enter your prompt
3. Select model (runway-gen3 or kling-1.5)
4. Configure parameters
5. Click "Generate Video"
```

## Testing Provider Availability

You can test if a provider's API is available:

```bash
# Test Runway
curl -X GET https://api.runwayml.com/v1/teams \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test Kling
curl -X GET https://api.klingai.com/v1/account \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test OpenAI Sora (will return 404 currently)
curl -X GET https://api.openai.com/v1/video/generations \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## When Will Sora Be Available?

OpenAI has announced Sora but hasn't released public API access yet. Based on their previous releases:

- **Early Access**: Available to select partners (current)
- **Beta**: Limited waitlist access (expected soon)
- **Public API**: General availability (TBD)

**Stay Updated:**
- Follow OpenAI's official announcements
- Check their API documentation: https://platform.openai.com/docs
- Monitor MediaRouter releases for updates

## What to Do Now

**Recommended Setup:**

1. **Use Runway or Kling** for immediate video generation
2. **Keep the OpenAI key** for other APIs (GPT, DALL-E, etc.)
3. **Star this repo** to get notified when Sora support is activated

## Updating Provider Implementations

When Sora's API launches, you can update MediaRouter:

```bash
# Pull latest version
git pull origin main

# Rebuild containers
docker compose down
docker compose build
docker compose up -d
```

The Sora provider will automatically work once the API is available.

## Need Help?

- **404 errors with Sora?** This is expected. Use Runway or Kling instead.
- **Other errors?** Check the logs: `docker compose logs backend`
- **Questions?** Open an issue on GitHub

---

**Last Updated**: October 2025

**Provider API Documentation:**
- Runway: https://docs.runwayml.com/
- Kling: https://docs.klingai.com/
- OpenAI: https://platform.openai.com/docs

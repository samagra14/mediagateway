# MediaRouter 🎬

> Open Source Video Generation Gateway - A unified API for multiple AI video generation providers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)

MediaRouter provides a unified OpenAI-compatible API for multiple video generation providers, with a beautiful playground UI for testing and experimentation. Use your own API keys (BYOK), maintain full control of your data, and run everything locally.

> **🎉 New**: OpenAI's Sora 2 API is now available! Generate videos with synced audio for $0.10/second.

## ✨ Features

- **🔌 Unified API**: Single OpenAI-compatible endpoint for multiple providers
- **🎨 Beautiful Playground**: Modern React UI with shadcn/ui components
- **🔑 BYOK Model**: Bring Your Own Keys - no vendor lock-in
- **🎯 Multiple Providers**: Support for Sora 2, Runway, Kling, and more
- **📊 Usage Tracking**: Monitor costs, generation times, and success rates
- **🎬 Video Gallery**: Browse and manage your generated videos
- **🚀 One Command Setup**: Get started instantly with Docker Compose
- **🔒 Secure**: Encrypted API key storage with industry-standard encryption

## 🎥 Supported Providers

| Provider | Models | Image-to-Video | Audio | API Status | Pricing |
|----------|--------|----------------|-------|------------|---------|
| **OpenAI Sora** | Sora 2, Sora 1 | ✅ | ✅ | ✅ **Public** | $0.10/sec |
| **Runway** | Gen-3, Gen-4 | ✅ | ❌ | ✅ **Public** | Usage-based |
| **Kling AI** | v1.5, v1.0 | ✅ | ❌ | ✅ **Public** | Credit-based |
| Pika Labs | Coming soon | ✅ | - | 🚧 Planned | - |
| Luma Dream Machine | Coming soon | ✅ | - | 🚧 Planned | - |

**All Three Providers Working**: Sora 2, Runway, and Kling all have public APIs available now!

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- API keys from your chosen providers ([Get API Keys](#getting-api-keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mediarouter.git
cd mediarouter

# Run the setup script
./setup.sh
```

That's it! The setup script will:
1. Create necessary directories
2. Generate secure encryption keys
3. Build Docker containers
4. Start all services

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs

### Manual Setup (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your encryption keys

# Run server
python run.py
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📖 Usage

### 1. Add API Keys

1. Navigate to **Settings** page
2. Click "Add API Key"
3. Select your provider (OpenAI, Runway, or Kling)
4. Paste your API key
5. Click "Add Key" to validate and save

### 2. Generate Videos

1. Go to the **Playground** page
2. Enter your prompt (e.g., "A serene sunset over mountains")
3. Select your desired model
4. Configure parameters:
   - **Duration**: 1-10 seconds
   - **Aspect Ratio**: 16:9, 9:16, or 1:1
   - **Seed**: Optional, for reproducibility
5. Click "Generate Video"
6. Wait for generation to complete
7. Download or view your video

### 3. Browse Gallery

1. Visit the **Gallery** page
2. View all your generated videos
3. Filter by provider or status
4. Download or delete videos

## 🔌 API Reference

### Generate Video

```bash
POST /v1/video/generations
Content-Type: application/json

{
  "model": "sora-2",
  "prompt": "A serene sunset over mountains",
  "duration": 5,
  "aspect_ratio": "16:9",
  "seed": 12345
}
```

**Response:**

```json
{
  "id": "gen_abc123",
  "object": "video.generation",
  "created": 1728234567,
  "model": "sora-2",
  "provider": "openai",
  "status": "processing",
  "prompt": "A serene sunset over mountains",
  "video": null,
  "usage": null
}
```

### Check Status

```bash
GET /v1/video/generations/{generation_id}
```

### List Generations

```bash
GET /v1/video/generations?limit=50&provider=openai&status=completed
```

### Full API Documentation

Visit http://localhost:3001/docs for interactive API documentation.

## 🔑 Getting API Keys

### OpenAI (Sora)

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create new API key
5. **Note**: Sora access may require waitlist approval

### Runway

1. Visit [Runway](https://runwayml.com/)
2. Sign up for an account
3. Go to Settings → API Keys
4. Generate new API key

### Kling AI

1. Visit [Kling AI](https://klingai.com/)
2. Create an account
3. Navigate to API section
4. Generate API key

## 🏗️ Architecture

```
mediarouter/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes and schemas
│   │   ├── providers/      # Provider adapters
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   └── db/             # Database setup
│   ├── requirements.txt
│   └── run.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   └── lib/           # Utilities and API client
│   └── package.json
├── storage/               # Video storage
├── docker-compose.yml     # Docker orchestration
└── setup.sh              # Setup script
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn src.main:app --reload --port 3001

# Run tests
pytest
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Adding a New Provider

1. Create a new provider file in `backend/src/providers/`
2. Implement the `VideoProvider` interface
3. Add provider to `PROVIDERS` dict in `__init__.py`
4. Add model mappings to `MODEL_PROVIDER_MAP`
5. Test the provider integration

Example:

```python
# backend/src/providers/newprovider.py
from .base import VideoProvider, VideoRequest, VideoResponse

class NewProvider(VideoProvider):
    @property
    def name(self) -> str:
        return "newprovider"

    @property
    def models(self) -> list[str]:
        return ["model-v1"]

    async def validate_key(self) -> bool:
        # Implement key validation
        pass

    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        # Implement video generation
        pass

    async def check_status(self, job_id: str) -> VideoResponse:
        # Implement status checking
        pass
```

## 🔒 Security

- API keys are encrypted using Fernet (symmetric encryption)
- Encryption keys are stored in `.env` (never commit to git)
- HTTPS recommended for production deployments
- CORS is configured for allowed origins only

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Stop existing containers
docker-compose down

# Or use different ports in docker-compose.yml
```

### Database Issues

```bash
# Reset database
rm storage/db.sqlite

# Restart backend
docker-compose restart backend
```

### Video Generation Stuck

- Check provider API status
- Verify API key validity in Settings
- Check backend logs: `docker-compose logs backend`
- Some providers have rate limits

## 📊 Usage Statistics

View detailed usage statistics in the Settings page:
- Total generations
- Cost breakdown by provider/model
- Average generation times
- Success/failure rates

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📞 Support

- 📧 Email: support@mediarouter.dev
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/mediarouter/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/mediarouter/discussions)

## 🗺️ Roadmap

- [ ] Additional providers (Pika, Luma, Haiper)
- [ ] Image-to-video support
- [ ] Video-to-video transformations
- [ ] Batch generation
- [ ] Webhook notifications
- [ ] Cost estimation before generation
- [ ] Public benchmarking dashboard
- [ ] CLI tool
- [ ] Python/TypeScript SDKs

## ⭐ Star History

If you find MediaRouter useful, please consider giving it a star on GitHub!

---

**Built with ❤️ by the open source community**

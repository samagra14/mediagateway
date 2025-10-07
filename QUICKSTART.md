# Quick Start Guide

Get MediaRouter running in 5 minutes!

## Option 1: Docker (Recommended)

```bash
# Run setup script
./setup.sh

# Wait for services to start (~30 seconds)
# Open http://localhost:3000
```

## Option 2: Manual Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Frontend (in new terminal)

```bash
cd frontend
npm install
npm run dev
```

## First Steps

1. **Open the app**: http://localhost:3000

2. **Add API Key**:
   - Go to Settings
   - Click "Add API Key"
   - Select provider (OpenAI/Runway/Kling)
   - Paste your API key
   - Click "Add Key"

3. **Generate Video**:
   - Go to Playground
   - Enter a prompt: "A serene sunset over mountains"
   - Select model
   - Click "Generate Video"
   - Wait for completion (~30-60 seconds)

4. **View Results**:
   - Video appears in Playground when done
   - Check Gallery to see all generations

## Getting API Keys

### OpenAI (Sora)
- Visit: https://platform.openai.com/api-keys
- Note: Sora access may be limited

### Runway
- Visit: https://app.runwayml.com/
- Go to Settings → API Keys

### Kling AI
- Visit: https://klingai.com/
- Navigate to API section

## Troubleshooting

**Port already in use?**
```bash
docker-compose down
# Or change ports in docker-compose.yml
```

**Can't connect to backend?**
```bash
# Check if backend is running
curl http://localhost:3001/health

# View logs
docker-compose logs backend
```

**No providers showing?**
- Make sure you added API keys in Settings
- Validate keys using "Test" button

## Next Steps

- Read the full [README.md](README.md)
- Check [API Documentation](http://localhost:3001/docs)
- Join our community discussions

Need help? Open an issue on GitHub!

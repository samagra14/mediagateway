# MediaRouter Project Structure

Complete overview of the project architecture and file organization.

## Directory Tree

```
mediarouter/
├── backend/                          # FastAPI Backend
│   ├── src/
│   │   ├── api/                     # API Layer
│   │   │   ├── routes.py           # API endpoints
│   │   │   └── schemas.py          # Pydantic schemas
│   │   ├── providers/              # Provider Adapters
│   │   │   ├── __init__.py         # Provider registry
│   │   │   ├── base.py             # Base provider interface
│   │   │   ├── sora.py             # OpenAI Sora provider
│   │   │   ├── runway.py           # Runway provider
│   │   │   └── kling.py            # Kling AI provider
│   │   ├── services/               # Business Logic
│   │   │   ├── encryption.py      # Key encryption
│   │   │   ├── key_manager.py     # API key management
│   │   │   └── video_storage.py   # Video file handling
│   │   ├── models/                 # Database Models
│   │   │   ├── __init__.py
│   │   │   ├── api_key.py         # API key model
│   │   │   ├── generation.py      # Generation model
│   │   │   └── usage_stat.py      # Usage statistics
│   │   ├── db/                     # Database
│   │   │   └── database.py        # SQLAlchemy setup
│   │   ├── config.py               # Configuration
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt            # Python dependencies
│   ├── run.py                      # Entry point
│   ├── Dockerfile                  # Docker config
│   └── .env.example               # Environment template
│
├── frontend/                        # React Frontend
│   ├── src/
│   │   ├── components/            # React Components
│   │   │   └── ui/               # shadcn/ui components
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── input.tsx
│   │   │       └── textarea.tsx
│   │   ├── pages/                # Page Components
│   │   │   ├── Playground.tsx   # Video generation UI
│   │   │   ├── Gallery.tsx      # Video gallery
│   │   │   └── Settings.tsx     # API key management
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts           # API client
│   │   │   └── utils.ts         # Helper functions
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── vite.config.ts           # Vite config
│   ├── tailwind.config.js       # Tailwind config
│   ├── postcss.config.js        # PostCSS config
│   ├── Dockerfile               # Docker config
│   ├── nginx.conf               # Nginx config
│   └── index.html               # HTML template
│
├── storage/                      # File Storage
│   ├── videos/                  # Generated videos
│   └── temp/                    # Temporary files
│
├── docker-compose.yml           # Docker orchestration
├── setup.sh                     # Setup script
├── Makefile                     # Make commands
├── package.json                 # Root package.json
├── .gitignore                   # Git ignore rules
├── .env.example                 # Environment template
│
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── CONTRIBUTING.md             # Contribution guide
├── LICENSE                     # MIT License
└── PROJECT_STRUCTURE.md        # This file
```

## Key Components

### Backend (FastAPI + Python)

**API Layer** (`src/api/`)
- `routes.py`: REST API endpoints (video generation, key management, etc.)
- `schemas.py`: Request/response validation schemas

**Providers** (`src/providers/`)
- Pluggable adapters for video generation services
- Each provider implements the `VideoProvider` interface
- Handles API communication, status polling, and response normalization

**Services** (`src/services/`)
- `encryption.py`: Fernet encryption for API keys
- `key_manager.py`: CRUD operations for API keys
- `video_storage.py`: Download and serve video files

**Models** (`src/models/`)
- SQLAlchemy ORM models for database tables
- `APIKey`: Store encrypted provider credentials
- `Generation`: Track video generation jobs
- `UsageStat`: Aggregate usage statistics

### Frontend (React + TypeScript)

**Pages** (`src/pages/`)
- `Playground.tsx`: Main video generation interface
- `Gallery.tsx`: Browse and manage generated videos
- `Settings.tsx`: API key management and configuration

**Components** (`src/components/ui/`)
- Reusable UI components from shadcn/ui
- Styled with Tailwind CSS

**Library** (`src/lib/`)
- `api.ts`: Type-safe API client
- `utils.ts`: Utility functions (classname merging, etc.)

## Data Flow

### Video Generation Flow

```
1. User submits prompt in Playground
   ↓
2. Frontend calls POST /v1/video/generations
   ↓
3. Backend creates Generation record (status: queued)
   ↓
4. Background task initiates provider API call
   ↓
5. Provider returns job ID
   ↓
6. Backend polls provider for status
   ↓
7. When complete, downloads video to storage/
   ↓
8. Updates Generation record (status: completed)
   ↓
9. Frontend polls GET /v1/video/generations/{id}
   ↓
10. Video URL returned to user
```

### API Key Flow

```
1. User adds API key in Settings
   ↓
2. Frontend validates input
   ↓
3. POST /v1/keys sent to backend
   ↓
4. Backend validates key with provider
   ↓
5. Key encrypted with Fernet
   ↓
6. Stored in database
   ↓
7. Success/failure returned to user
```

## Database Schema

### api_keys
- `id`: Integer (Primary Key)
- `provider`: String (openai, runway, kling)
- `encrypted_key`: String (Fernet encrypted)
- `status`: Enum (active, invalid, quota_exceeded, revoked)
- `last_validated`: DateTime
- `created_at`: DateTime
- `updated_at`: DateTime

### generations
- `id`: String (Primary Key, gen_xxxxx)
- `provider`: String
- `model`: String
- `prompt`: String
- `parameters`: JSON
- `video_url`: String (nullable)
- `video_path`: String (nullable)
- `status`: Enum (queued, processing, completed, failed, cancelled)
- `error_message`: String (nullable)
- `cost`: Float (nullable)
- `duration_seconds`: Float (nullable)
- `generation_time`: Float (nullable)
- `width`: Integer (nullable)
- `height`: Integer (nullable)
- `provider_job_id`: String (nullable)
- `created_at`: DateTime
- `updated_at`: DateTime
- `completed_at`: DateTime (nullable)

### usage_stats
- `id`: Integer (Primary Key)
- `provider`: String
- `model`: String
- `count`: Integer
- `total_cost`: Float
- `avg_time`: Float
- `success_count`: Integer
- `failure_count`: Integer
- `date`: Date

## API Endpoints

### Video Generation
- `POST /v1/video/generations` - Create generation
- `GET /v1/video/generations/{id}` - Get generation status
- `GET /v1/video/generations` - List generations
- `DELETE /v1/video/generations/{id}` - Delete generation

### API Keys
- `POST /v1/keys` - Add API key
- `GET /v1/keys` - List API keys
- `DELETE /v1/keys/{id}` - Delete API key
- `POST /v1/keys/{id}/validate` - Validate API key

### Providers
- `GET /v1/providers` - List available providers

### Usage
- `GET /v1/usage/stats` - Get usage statistics

### System
- `GET /` - API info
- `GET /health` - Health check
- `GET /videos/{filename}` - Serve video files

## Environment Variables

See `.env.example` for all configuration options.

**Required:**
- `ENCRYPTION_KEY`: Key for encrypting API keys
- `SECRET_KEY`: Session secret

**Optional:**
- `DATABASE_URL`: Database connection string
- `STORAGE_PATH`: Video storage directory
- `PORT`: Backend port (default: 3001)
- `FRONTEND_URL`: Frontend URL for CORS

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104
- **Database**: SQLite (SQLAlchemy ORM)
- **Async**: asyncio, httpx
- **Encryption**: cryptography (Fernet)
- **Validation**: Pydantic

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.2
- **Build Tool**: Vite 5.0
- **UI**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS 3.3
- **Routing**: React Router 6.20

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (frontend proxy)

## Development Commands

```bash
# Setup
./setup.sh                  # Initial setup
make setup                  # Alternative

# Development
make dev                    # Run both servers
make dev-backend            # Run backend only
make dev-frontend           # Run frontend only

# Docker
make docker-up              # Start containers
make docker-down            # Stop containers
make docker-logs            # View logs
make docker-build           # Rebuild images

# Cleanup
make clean                  # Remove generated files
```

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## Deployment

### Production Checklist
- [ ] Change default encryption keys
- [ ] Enable HTTPS
- [ ] Configure CORS for production domain
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set up proper logging
- [ ] Configure monitoring
- [ ] Set up backups for database and videos
- [ ] Use cloud storage (S3/R2) for videos
- [ ] Set up CDN for video delivery

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

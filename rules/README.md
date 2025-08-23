# Rules Service for Barbershop SaaS

A production-ready FastAPI backend for managing subscription plans, addons, and entitlements for a barbershop SaaS platform.

## Features

- **Plan Management**: CRUD operations for subscription plans (Silver, Gold, Platinum)
- **Addon Management**: CRUD operations for addon features (AI Booking, Variable Pricing, etc.)
- **Tenant Assignments**: Assign plans and addons to tenants
- **Entitlements Computation**: Real-time computation of tenant entitlements
- **Redis Caching**: High-performance caching with ETag support
- **Database Migrations**: Alembic with autogenerate support
- **Authentication**: Simple header-based auth for development
- **Comprehensive Testing**: 80%+ coverage with pytest

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI + Pydantic v2
- **Database**: PostgreSQL via SQLAlchemy 2.x
- **Migrations**: Alembic (autogenerate enabled)
- **Cache**: Redis (redis-py)
- **Testing**: pytest + httpx + pytest-asyncio
- **Lint/Format**: ruff + black
- **Container**: Docker + docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker

1. **Clone and start the services**:

   ```bash
   docker compose up --build
   ```

2. **Check health**:

   ```bash
   curl http://localhost:8000/health
   ```

3. **View API documentation**:
   ```
   http://localhost:8000/docs
   ```

### Local Development

1. **Install dependencies**:

   ```bash
   pip install -e .
   ```

2. **Set up environment**:

   ```bash
   export DATABASE_URL="postgresql+psycopg://rules:rules@localhost:5432/rules"
   export REDIS_URL="redis://localhost:6379/0"
   ```

3. **Run migrations**:

   ```bash
   alembic upgrade head
   ```

4. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Examples

### Admin Operations

#### Create Plans

```bash
# Create Silver Plan
curl -X POST "http://localhost:8000/admin/plans/" \
  -H "X-Internal-Role: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "silver",
    "name": "Silver Plan",
    "limits_json": {"locations": 1, "stylists": 5},
    "features_json": {"basic_reporting": true}
  }'

# Create Gold Plan
curl -X POST "http://localhost:8000/admin/plans/" \
  -H "X-Internal-Role: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "gold",
    "name": "Gold Plan",
    "limits_json": {"locations": 2, "stylists": 10},
    "features_json": {
      "loyalty_points": true,
      "reviews": true,
      "advanced_analytics": true
    }
  }'
```

#### Create Addons

```bash
# Create AI Booking Addon
curl -X POST "http://localhost:8000/admin/addons/" \
  -H "X-Internal-Role: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ai_booking",
    "name": "AI Booking",
    "meta_json": {"enabled": true}
  }'

# Create Value Pack Addon
curl -X POST "http://localhost:8000/admin/addons/" \
  -H "X-Internal-Role: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "value_pack",
    "name": "Value Pack",
    "meta_json": {"packages": true, "upsell": true}
  }'
```

### Tenant Operations

#### Assign Plan to Tenant

```bash
curl -X PUT "http://localhost:8000/tenants/ten_123/plan" \
  -H "X-Internal-Service: billing-service" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_code": "gold",
    "meta": {"billing_cycle": "monthly"}
  }'
```

#### Add Addons to Tenant

```bash
curl -X PUT "http://localhost:8000/tenants/ten_123/addons" \
  -H "X-Internal-Service: billing-service" \
  -H "Content-Type: application/json" \
  -d '{
    "add": ["ai_booking", "value_pack"],
    "remove": [],
    "upsert": []
  }'
```

#### Get Tenant Assignments

```bash
curl -X GET "http://localhost:8000/tenants/ten_123/assignments" \
  -H "X-Internal-Service: billing-service"
```

### Entitlements

#### Get Computed Entitlements

```bash
curl -X GET "http://localhost:8000/entitlements/ten_123" \
  -H "X-Internal-Service: frontend-service"
```

Example Response:

```json
{
  "tenant_id": "ten_123",
  "plan": "gold",
  "limits": { "locations": 2, "stylists": 10 },
  "features": {
    "loyalty_points": true,
    "reviews": true,
    "advanced_analytics": true,
    "ai_booking": true,
    "variable_pricing": false
  },
  "addons": {
    "ai_booking": true,
    "value_pack": {
      "packages": true,
      "upsell": true,
      "waitlist": true,
      "gift_cards": true
    }
  },
  "billing": {
    "per_stylist_fee": 15,
    "per_location_fee": 99,
    "discount_tier": 0.0
  },
  "version": 3,
  "updated_at": "2025-01-21T18:05:00Z",
  "ttl_hint_sec": 900
}
```

## Plan Features

### Silver Plan

- **Limits**: 1 location, 5 stylists
- **Features**: basic_reporting=true

### Gold Plan

- **Limits**: 2 locations, 10 stylists
- **Features**: loyalty_points, reviews, advanced_analytics, stylist_matching, family_booking

### Platinum Plan

- **Limits**: 3 locations, 20 stylists
- **Features**: online_store, tiered_loyalty, memberships, smart_no_shows, dynamic_pricing, ai_promotions, staff_utilization, offline_mode, data_export, voice_assistant

## Addon Features

- **ai_booking**: Enables AI-powered booking features
- **variable_pricing**: Enables dynamic pricing capabilities
- **value_pack**: Enables packages, upsell, waitlist; includes gift_cards on Gold+
- **family_booking**: Enables family booking (Silver plan only)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_admin_plans.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Architecture

### Project Structure

```
rules/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database configuration
│   ├── cache.py             # Redis cache utilities
│   ├── events.py            # Event handling
│   ├── deps.py              # Dependencies and auth
│   ├── routers/             # API route handlers
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Service orchestration
└── pyproject.toml           # Project configuration
```

### Key Components

1. **Models**: SQLAlchemy models for plans, addons, tenant assignments
2. **Services**: Business logic for CRUD operations and entitlements computation
3. **Routers**: FastAPI route handlers with authentication
4. **Cache**: Redis-based caching with ETag support
5. **Events**: Event emission for plan/addon changes

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging level
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 900)

### Authentication Headers

- `X-Internal-Role: admin` - For admin CRUD endpoints
- `X-Internal-Service: <service-name>` - For internal service endpoints

## Production Considerations

1. **Security**: Replace header-based auth with proper JWT/OAuth
2. **Monitoring**: Add metrics collection and health checks
3. **Scaling**: Consider Redis clustering for high availability
4. **Backup**: Implement database backup strategies
5. **CI/CD**: Set up automated testing and deployment pipelines

## License

MIT License

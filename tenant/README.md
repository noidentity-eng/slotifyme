# Tenant Service

A FastAPI-based tenant management service for the barbershop platform.

## Features

- **Tenant Management**: Create, update, and manage tenants with unique slugs
- **Location Management**: Manage locations within tenants with timezone support
- **User Linking**: Link users to tenants with different roles (owner, staff, stylist)
- **Public APIs**: Secure public endpoints for tenant and location information
- **Idempotency**: Support for idempotent operations via Idempotency-Key header
- **Data Classification**: Public/private field control for data visibility
- **Observability**: Structured logging, request IDs, and OpenTelemetry hooks
- **Rules Integration**: Optional integration with rules service for limits

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI + Pydantic v2
- **Database**: PostgreSQL with SQLAlchemy 2.x + Alembic migrations
- **Cache**: Redis (for idempotency)
- **Auth**: Header-based guards (X-Internal-Role, X-Internal-Service)
- **Testing**: pytest + httpx
- **Formatting**: black + ruff
- **Deployment**: Docker + ECS Fargate

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone and setup**:

   ```bash
   git clone <repository>
   cd tenant
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

2. **Start services**:

   ```bash
   docker-compose up -d
   ```

3. **Run migrations**:

   ```bash
   alembic upgrade head
   ```

4. **Start the service**:

   ```bash
   uvicorn tenant.app.main:app --reload
   ```

5. **Access the API**:
   - API Documentation: http://localhost:8002/docs
   - Health Check: http://localhost:8002/health

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tenant
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
RULES_BASE_URL=http://localhost:8001  # Optional
```

## API Endpoints

### Superadmin Endpoints (require X-Internal-Role: admin)

#### Tenants

- `POST /tenants` - Create tenant (idempotent)
- `GET /tenants` - List tenants with pagination
- `GET /tenants/{tenant_id}` - Get tenant by ID
- `PUT /tenants/{tenant_id}` - Update tenant

#### Locations

- `POST /tenants/{tenant_id}/locations` - Create location (idempotent)
- `GET /tenants/{tenant_id}/locations` - List locations
- `GET /locations/{location_id}` - Get location by ID
- `PUT /locations/{location_id}` - Update location

#### User Links

- `POST /tenants/{tenant_id}/users` - Link user to tenant
- `DELETE /tenants/{tenant_id}/users/{user_id}` - Unlink user
- `GET /tenants/{tenant_id}/users` - List users by role
- `GET /tenants/{tenant_id}/users/stats` - Get tenant statistics

### Internal Endpoints (require X-Internal-Service header)

#### Public Views

- `GET /public/tenants/{slug}` - Get public tenant info
- `GET /public/tenants/{tenant_slug}/locations` - Get public locations
- `GET /public/tenants/{tenant_slug}/locations/{location_slug}` - Get public location

#### Statistics

- `GET /internal/tenants/{tenant_id}/stats` - Get tenant statistics

### Health

- `GET /health` - Health check

## Data Model

### Tenants

- `id` (ULID, PK)
- `slug` (unique, kebab-case)
- `name`
- `status` (active|disabled|suspended)
- `theme_json` (branding data)
- `created_at`, `updated_at`

### Locations

- `id` (ULID, PK)
- `tenant_id` (FK to tenants)
- `slug` (unique per tenant)
- `name`
- `address_json` (structured address)
- `timezone` (IANA timezone)
- `phone` (private)
- `phone_public` (boolean flag)
- `status` (active|disabled)
- `created_at`, `updated_at`

### Tenant Users

- `tenant_id` (FK, part of composite PK)
- `user_id` (part of composite PK)
- `role` (owner|staff|stylist)
- `created_at`

### Data Classification

- `table_name`, `column_name` (composite PK)
- `classification` (public|private|sensitive)
- `visibility_controlled` (boolean)

## Authentication

The service uses header-based authentication:

- **Superadmin endpoints**: Require `X-Internal-Role: admin`
- **Internal endpoints**: Require `X-Internal-Service: <service-name>`
- **Request tracking**: Uses `X-Request-ID` header

## Idempotency

Create endpoints support idempotency via the `Idempotency-Key` header:

```bash
curl -X POST /tenants \
  -H "Idempotency-Key: unique-key-123" \
  -H "X-Internal-Role: admin" \
  -d '{"name": "My Tenant", "slug": "my-tenant"}'
```

## Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=tenant --cov-report=html

# Run specific test file
pytest tests/test_tenants.py
```

## Development

### Code Quality

```bash
# Format code
black tenant/

# Lint code
ruff check tenant/

# Type checking
mypy tenant/
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

## Deployment

### Docker

```bash
# Build image
docker build -t tenant-service .

# Run container
docker run -p 8002:8002 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  tenant-service
```

### ECS Fargate

The service is designed to be deployed on AWS ECS Fargate with:

- **Container Port**: 8002
- **Health Check**: `/health` endpoint
- **Environment Variables**: Set via AWS Secrets Manager
- **Service Discovery**: Cloud Map registration as `tenant.barbershop.local`

## Smoke Test

Quick end-to-end test flow:

```bash
# 1. Create tenant
curl -X POST http://localhost:8002/tenants \
  -H "Content-Type: application/json" \
  -H "X-Internal-Role: admin" \
  -H "Idempotency-Key: test-tenant-1" \
  -d '{"name": "Test Barbershop", "slug": "test-barbershop"}'

# 2. Create location
curl -X POST http://localhost:8002/tenants/{tenant_id}/locations \
  -H "Content-Type: application/json" \
  -H "X-Internal-Role: admin" \
  -H "Idempotency-Key: test-location-1" \
  -d '{"name": "Downtown", "slug": "downtown", "timezone": "America/Los_Angeles"}'

# 3. Link owner
curl -X POST http://localhost:8002/tenants/{tenant_id}/users \
  -H "Content-Type: application/json" \
  -H "X-Internal-Role: admin" \
  -d '{"user_id": "usr_123", "role": "owner"}'

# 4. Test public endpoints
curl -H "X-Internal-Service: test" http://localhost:8002/public/tenants/test-barbershop
curl -H "X-Internal-Service: test" http://localhost:8002/public/tenants/test-barbershop/locations
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## License

MIT License

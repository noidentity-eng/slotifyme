# Router/Slug Service

A high-performance URL routing service for the Barbershop SaaS platform that provides slug mapping, resolution, and manifest publishing capabilities.

## Features

- **Admin CRUD**: Create, update, and delete slug mappings (host + path → resource)
- **Resolve API**: Map pretty URLs to internal resource IDs for edge/proxy services
- **Manifest Publishing**: Generate compact JSON manifests for edge caches/workers
- **Conflict Detection**: Prevent duplicate active mappings with proper conflict handling
- **Tenant Validation**: Optional integration with Tenant service for existence checks
- **Caching**: Redis-based caching with configurable TTL
- **Idempotency**: Support for idempotent operations via Idempotency-Key header

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional, for caching)
- Docker & Docker Compose (for local development)

### Local Development

1. **Clone and setup**:

   ```bash
   git clone <repository>
   cd router
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Environment setup**:

   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

3. **Database setup**:

   ```bash
   alembic upgrade head
   ```

4. **Run the service**:
   ```bash
   uvicorn app.main:app --reload --port 8003
   ```

### Docker Development

```bash
docker-compose up -d
```

The service will be available at `http://localhost:8003`

## API Documentation

Once running, visit:

- **OpenAPI Docs**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## Core APIs

### Health Check

```bash
GET /health
```

### Admin APIs (requires admin authentication)

#### Create Slug Mapping

```bash
POST /admin/slugs
Content-Type: application/json
X-Internal-Role: admin
Idempotency-Key: <unique-key>

{
  "host": "slotifyme.com",
  "path": "/barbershop-a/downtown",
  "resource_type": "location",
  "resource_id": "loc_456",
  "tenant_id": "ten_123",
  "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
  "status": "active"
}
```

#### Update Slug Mapping

```bash
PUT /admin/slugs/{id}
Content-Type: application/json
X-Internal-Role: admin

{
  "canonical_url": "https://slotifyme.com/barbershop-a/downtown-location"
}
```

#### Delete Slug Mapping

```bash
DELETE /admin/slugs/{id}?soft=true
X-Internal-Role: admin
```

#### List Slug Mappings

```bash
GET /admin/slugs?host=slotifyme.com&tenant_id=ten_123&status=active&page=1&page_size=20
X-Internal-Role: admin
```

#### Check Availability

```bash
GET /admin/slugs/check-availability?host=slotifyme.com&path=/barbershop-a/downtown
X-Internal-Role: admin
```

### Resolve API (internal/edge services)

#### Resolve URL

```bash
GET /resolve?host=slotifyme.com&path=/barbershop-a/downtown
X-Internal-Service: edge
```

Response:

```json
{
  "match": true,
  "resource": {
    "type": "location",
    "id": "loc_456"
  },
  "tenant_id": "ten_123",
  "version": 3,
  "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
  "cache": {
    "max_age": 600,
    "etag": "W/\"loc_456-v3\""
  }
}
```

### Publish API (manifest generation)

#### Generate Manifest

```bash
POST /publish
X-Internal-Role: admin
```

Response:

```json
{
  "generated_at": "2025-08-22T10:05:00Z",
  "count": 1234,
  "items": [
    ["slotifyme.com", "/barbershop-a", "tenant", "ten_123", 5],
    ["slotifyme.com", "/barbershop-a/downtown", "location", "loc_456", 3]
  ],
  "s3_url": "https://s3.amazonaws.com/bucket/router/manifest.json",
  "etag": "abc123"
}
```

## Configuration

### Environment Variables

| Variable            | Description                    | Default  |
| ------------------- | ------------------------------ | -------- |
| `DATABASE_URL`      | PostgreSQL connection string   | Required |
| `REDIS_URL`         | Redis connection string        | Optional |
| `TENANT_BASE_URL`   | Tenant service base URL        | Optional |
| `PUBLISH_S3_BUCKET` | S3 bucket for manifest uploads | Optional |
| `LOG_LEVEL`         | Logging level                  | `INFO`   |

### Authentication

The service uses header-based authentication:

- **Admin access**: `X-Internal-Role: admin`
- **Internal service access**: `X-Internal-Service: <service-name>`

## Data Model

### slug_map

- `id` (PK): Unique identifier
- `host` (text): Domain name (e.g., slotifyme.com)
- `path` (text): URL path with leading slash
- `resource_type` (enum): tenant, location, stylist, service
- `resource_id` (text): Canonical ID from owning service
- `tenant_id` (text, nullable): Convenience for queries
- `version` (int): Cache invalidation version
- `status` (enum): active, draft, deleted
- `canonical_url` (text): SEO-friendly URL
- `created_at`, `updated_at` (timestamps)

### slug_history

- `id` (PK): Unique identifier
- `slug_map_id` (FK): Reference to slug_map
- `old_values_json` (jsonb): Previous values
- `new_values_json` (jsonb): New values
- `changed_at` (timestamp): When change occurred
- `actor` (text): Who made the change

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_admin_slugs.py
```

## Deployment

### Docker

```bash
docker build -t router .
docker run -p 8003:8003 router
```

### AWS ECS

The service includes Terraform configuration for AWS ECS Fargate deployment:

```bash
cd infra/aws/router-ecs
terraform init
terraform plan
terraform apply
```

## Development Workflow

1. **Code formatting**: `ruff check . && ruff format .`
2. **Type checking**: `mypy app/`
3. **Tests**: `pytest`
4. **Database migrations**: `alembic revision --autogenerate -m "description"`

## Architecture

The service follows a clean architecture pattern:

- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic validation schemas
- **Services**: Business logic layer
- **Routers**: FastAPI route handlers
- **Dependencies**: Shared utilities and dependencies

## Monitoring & Observability

- **Request IDs**: Automatically generated for request tracing
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Built-in health endpoint
- **Metrics**: Request timing and error rates

## Security

- Header-based authentication for internal services
- Input validation via Pydantic schemas
- SQL injection protection via SQLAlchemy
- Rate limiting (configurable)
- CORS configuration for web clients

## Performance

- Redis caching for resolve operations (TTL: 5-15 minutes)
- Database connection pooling
- Efficient queries with proper indexing
- Compact manifest format for edge distribution

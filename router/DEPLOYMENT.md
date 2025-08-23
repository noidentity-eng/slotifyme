# Router Service Deployment Guide

This guide provides step-by-step instructions for deploying the Router/Slug Service in different environments.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL database
- Redis (optional, for caching)
- AWS CLI (for production deployment)
- Terraform (for infrastructure deployment)

## Local Development Setup

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd router

# Run the development setup script
./scripts/dev-setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://router:password@localhost:5432/router

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# External Services
TENANT_BASE_URL=http://tenant-service:8001

# S3 Configuration (optional)
PUBLISH_S3_BUCKET=slotifyme-router-manifests

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
```

### 3. Start Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload --port 8003
```

### 4. Verify Installation

- Health check: http://localhost:8003/health
- API documentation: http://localhost:8003/docs
- ReDoc documentation: http://localhost:8003/redoc

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_admin_slugs.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8003/health

# Create slug mapping (requires admin auth)
curl -X POST http://localhost:8003/admin/slugs \
  -H "Content-Type: application/json" \
  -H "X-Internal-Role: admin" \
  -d '{
    "host": "slotifyme.com",
    "path": "/barbershop-a/downtown",
    "resource_type": "location",
    "resource_id": "loc_456",
    "tenant_id": "ten_123",
    "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
    "status": "active"
  }'

# Resolve URL (requires internal service auth)
curl "http://localhost:8003/resolve?host=slotifyme.com&path=/barbershop-a/downtown" \
  -H "X-Internal-Service: edge"

# Publish manifest (requires admin auth)
curl -X POST http://localhost:8003/publish \
  -H "X-Internal-Role: admin"
```

## Production Deployment

### 1. AWS Infrastructure Setup

```bash
cd infra/aws/router-ecs

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your VPC and subnet IDs

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply
```

### 2. Build and Push Docker Image

```bash
# Build image
docker build -t slotifyme/router:latest .

# Tag for ECR
docker tag slotifyme/router:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/slotifyme/router:latest

# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com

# Push to ECR
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/slotifyme/router:latest
```

### 3. Configure Secrets

```bash
# Database URL
aws secretsmanager put-secret-value \
  --secret-id router/database-url \
  --secret-string "postgresql+asyncpg://user:password@host:5432/database"

# Redis URL
aws secretsmanager put-secret-value \
  --secret-id router/redis-url \
  --secret-string "redis://host:6379"
```

### 4. Deploy Application

```bash
# Update ECS service
aws ecs update-service \
  --cluster router-cluster \
  --service router-service \
  --force-new-deployment
```

## Monitoring and Observability

### CloudWatch Logs

Logs are automatically sent to CloudWatch Log Group: `/ecs/router`

### Health Checks

- Application health: `/health`
- ECS health checks configured in task definition
- ALB health checks configured for target group

### Metrics

- ECS service metrics in CloudWatch
- Application metrics via structured logging
- Request timing via `X-Process-Time` header

## Security

### Authentication

- Admin access: `X-Internal-Role: admin`
- Internal service access: `X-Internal-Service: <service-name>`

### Network Security

- ECS tasks run in private subnets
- ALB in public subnets with security groups
- Database access via VPC endpoints (recommended)

### Secrets Management

- Database and Redis URLs stored in AWS Secrets Manager
- ECS tasks have IAM roles for secret access

## Scaling

### Horizontal Scaling

```bash
# Scale ECS service
aws ecs update-service \
  --cluster router-cluster \
  --service router-service \
  --desired-count 4
```

### Auto Scaling

Configure ECS Service Auto Scaling based on:

- CPU utilization
- Memory utilization
- Custom metrics

## Backup and Recovery

### Database Backup

- Enable automated backups on RDS
- Configure backup retention period
- Test restore procedures regularly

### Application Data

- Slug mappings stored in PostgreSQL
- History audit trail maintained
- Cache data in Redis (ephemeral)

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   - Check DATABASE_URL in Secrets Manager
   - Verify VPC security groups
   - Check RDS instance status

2. **Cache Issues**

   - Verify Redis connection
   - Check Redis memory usage
   - Review cache TTL settings

3. **Service Discovery Issues**
   - Verify Cloud Map namespace
   - Check DNS resolution
   - Review service registration

### Debug Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster router-cluster --services router-service

# View CloudWatch logs
aws logs tail /ecs/router --follow

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

## Maintenance

### Regular Tasks

- Monitor CloudWatch metrics
- Review and rotate secrets
- Update dependencies
- Review and clean up old logs
- Test disaster recovery procedures

### Updates

1. Build new Docker image
2. Update ECS task definition
3. Deploy with blue-green strategy
4. Monitor health checks
5. Rollback if issues detected

## Support

For issues and questions:

- Check CloudWatch logs
- Review application metrics
- Contact the development team
- Refer to API documentation at `/docs`

# AWS Configuration
aws_region = "us-west-2"

# Project Configuration
project_name = "barbershop"
service_name = "rules"

# Network Configuration (you'll need to update these with your actual VPC and subnet IDs)
vpc_id = "vpc-xxxxxxxxx"  # Replace with your VPC ID
subnet_ids = [
  "subnet-xxxxxxxxx",  # Replace with your subnet IDs
  "subnet-yyyyyyyyy"
]

# Container Configuration
container_port = 8000
container_cpu = 256
container_memory = 512
desired_count = 1

# Service Discovery Configuration
private_dns_namespace_name = "barbershop.local"
service_discovery_service_name = "rules"

# Database Configuration
database_url = "postgresql+psycopg://user:pwd@db_url:5432/barbershop"

# Redis Configuration (you may want to use ElastiCache in production)
redis_url = "redis://localhost:6379/0"

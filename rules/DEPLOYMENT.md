# Rules Service Deployment Guide

This guide will help you deploy the Rules Service to AWS ECS Fargate with RDS PostgreSQL and Cloud Map service discovery.

## Prerequisites

1. **AWS CLI** installed and configured
2. **Terraform** installed (version >= 1.0)
3. **Docker** installed
4. **Python** with virtual environment activated

## AWS Credentials

The deployment uses the following AWS credentials:

- **Access Key ID**:
- **Secret Access Key**:
- **Region**: us-west-2

## Database Configuration

The service connects to:

- **RDS Instance**: db_url
- **Database**: barbershop
- **Username**: uesr
- **Password**: password

## Deployment Steps

### 1. Update Network Configuration

Edit `infra/aws/rules-ecs/terraform.tfvars` and update:

- `vpc_id` with your VPC ID
- `subnet_ids` with your subnet IDs

### 2. Deploy Infrastructure

```bash
cd infra/aws/rules-ecs

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
```

### 3. Run Database Migrations

```bash
# From the project root
./migrate_db.sh
```

### 4. Deploy the Application

```bash
# From the project root
./deploy.sh
```

## Service Endpoints

After deployment, the service will be available at:

- **External (via ALB)**: http://[ALB-DNS-NAME]
- **Internal (VPC only)**: rules.barbershop.local

## Service Discovery

The service is registered in AWS Cloud Map with:

- **Namespace**: barbershop.local
- **Service**: rules
- **Full DNS**: rules.barbershop.local

Other services in the same VPC can reach the Rules service using the internal DNS name.

## Monitoring

### Check Service Status

```bash
aws ecs describe-services --cluster rules-cluster --services rules-service
```

### View Logs

```bash
aws logs tail /ecs/rules --follow
```

### Health Check

```bash
curl http://[ALB-DNS-NAME]/health
```

## Security Groups

The service allows:

- **External traffic**: Via ALB (HTTP/HTTPS)
- **Internal traffic**: From specified security groups (configurable via `allow_from_sg_ids`)

## Scaling

The service is configured with:

- **Min tasks**: 1
- **Max tasks**: 3
- **Desired tasks**: 1

You can adjust these values in `terraform.tfvars`.

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Verify RDS security group allows connections from ECS tasks
   - Check database credentials

2. **Service Discovery Not Working**

   - Ensure VPC DNS resolution is enabled
   - Verify security groups allow internal communication

3. **Container Health Check Failing**
   - Check application logs in CloudWatch
   - Verify health endpoint is responding

### Useful Commands

```bash
# Check ECS task status
aws ecs list-tasks --cluster rules-cluster

# View task logs
aws logs describe-log-streams --log-group-name /ecs/rules

# Test internal DNS resolution
nslookup rules.barbershop.local
```

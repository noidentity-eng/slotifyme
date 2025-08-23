variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "barbershop"
}

variable "service_name" {
  description = "Name of the service"
  type        = string
  default     = "rules"
}

variable "vpc_id" {
  description = "VPC ID where the service will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs where the service will be deployed"
  type        = list(string)
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "CPU units for the container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory for the container in MiB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 1
}

variable "max_count" {
  description = "Maximum number of tasks"
  type        = number
  default     = 3
}

variable "min_count" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "private_dns_namespace_id" {
  description = "Existing Cloud Map private DNS namespace ID (if you already have barbershop.local). If empty, we'll create one."
  type        = string
  default     = ""
}

variable "private_dns_namespace_name" {
  description = "Name of the private DNS namespace to create/use (e.g., barbershop.local). Ignored if private_dns_namespace_id is set."
  type        = string
  default     = "barbershop.local"
}

variable "service_discovery_service_name" {
  description = "Service discovery record name for this service (left label)."
  type        = string
  default     = "rules"
}

variable "allow_from_sg_ids" {
  description = "Security group IDs that may call the Rules service directly by IP/DNS (optional). If empty, no extra ingress besides ALB."
  type        = list(string)
  default     = []
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  default     = "postgresql+psycopg://user:pwd@db_url:5432/barbershop"
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  default     = "redis://localhost:6379/0"
}

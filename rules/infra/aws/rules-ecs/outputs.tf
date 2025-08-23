output "private_dns_namespace_id" {
  value       = local.effective_namespace_id
  description = "Cloud Map private DNS namespace ID (Route53 PHZ)."
}

output "service_discovery_service_arn" {
  value       = aws_service_discovery_service.rules.arn
  description = "Cloud Map service ARN for Rules."
}

output "private_dns_name" {
  value       = "${var.service_discovery_service_name}.${var.private_dns_namespace_name}"
  description = "Internal DNS name other services can use."
}

output "alb_dns_name" {
  value       = aws_lb.rules.dns_name
  description = "DNS name of the Application Load Balancer."
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.rules.repository_url
  description = "URL of the ECR repository."
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.rules.name
  description = "Name of the ECS cluster."
}

output "ecs_service_name" {
  value       = aws_ecs_service.rules.name
  description = "Name of the ECS service."
}

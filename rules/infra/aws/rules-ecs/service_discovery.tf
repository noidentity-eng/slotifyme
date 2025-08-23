locals {
  sd_namespace_id = var.private_dns_namespace_id
}

# Create a private DNS namespace if one wasn't provided
resource "aws_service_discovery_private_dns_namespace" "ns" {
  count = local.sd_namespace_id == "" ? 1 : 0
  name  = var.private_dns_namespace_name
  vpc   = var.vpc_id
}

# Use existing or newly created namespace ID
locals {
  effective_namespace_id = local.sd_namespace_id != "" ? local.sd_namespace_id : aws_service_discovery_private_dns_namespace.ns[0].id
}

resource "aws_service_discovery_service" "rules" {
  name = var.service_discovery_service_name

  dns_config {
    namespace_id = local.effective_namespace_id
    routing_policy = "MULTIVALUE"

    dns_records {
      type = "A"
      ttl  = 5
    }
  }

  # Optional custom health check config for ECS-managed instances
  health_check_custom_config {
    failure_threshold = 1
  }

  tags = {
    Project = var.project_name
    Service = var.service_name
  }
}

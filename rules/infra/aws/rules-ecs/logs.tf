# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "rules" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 7

  tags = {
    Project = var.project_name
    Service = var.service_name
  }
}

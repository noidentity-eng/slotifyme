# ECR Repository
resource "aws_ecr_repository" "rules" {
  name                 = "${var.service_name}-repository"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = var.project_name
    Service = var.service_name
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "rules" {
  repository = aws_ecr_repository.rules.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 images"
        selection = {
          tagStatus     = "untagged"
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

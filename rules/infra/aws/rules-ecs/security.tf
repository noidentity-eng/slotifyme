# Security group for the Rules service
resource "aws_security_group" "rules_sg" {
  name_prefix = "${var.service_name}-sg-"
  vpc_id      = var.vpc_id

  # Allow inbound traffic from ALB
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # Allow outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.service_name}-security-group"
    Project = var.project_name
    Service = var.service_name
  }
}

# Security group for ALB
resource "aws_security_group" "alb_sg" {
  name_prefix = "${var.service_name}-alb-sg-"
  vpc_id      = var.vpc_id

  # Allow inbound HTTP traffic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound HTTPS traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound traffic to ECS tasks
  egress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.rules_sg.id]
  }

  tags = {
    Name    = "${var.service_name}-alb-security-group"
    Project = var.project_name
    Service = var.service_name
  }
}

# Allow other internal services to call the Rules service directly
resource "aws_security_group_rule" "allow_from_callers" {
  count                    = length(var.allow_from_sg_ids) > 0 ? 1 : 0
  type                     = "ingress"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rules_sg.id
  source_security_group_id = element(var.allow_from_sg_ids, 0)
}

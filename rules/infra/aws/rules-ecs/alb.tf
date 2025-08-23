# Application Load Balancer
resource "aws_lb" "rules" {
  name               = "${var.service_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = false

  tags = {
    Project = var.project_name
    Service = var.service_name
  }
}

# ALB Target Group
resource "aws_lb_target_group" "rules" {
  name        = "${var.service_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Project = var.project_name
    Service = var.service_name
  }
}

# ALB Listener
resource "aws_lb_listener" "rules" {
  load_balancer_arn = aws_lb.rules.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.rules.arn
  }
}

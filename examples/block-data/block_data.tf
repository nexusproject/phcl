resource "aws_security_group" "web_security_group" {
  name = "web"
  description = "Web access"
  vpc_id = "vpc-0123456789abcdef0"
  tags = {
    Project = "phcl"
    ManagedBy = "PHCL"
    Environment = "dev"
    Component = "web"
    Name = "web-sg"
  }

  ingress {
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
    from_port = 80
    to_port = 80
  }

  ingress {
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
    from_port = 443
    to_port = 443
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "rendered_tags" {
  value = {
    Project = "phcl"
    ManagedBy = "PHCL"
    Environment = "dev"
    Component = "web"
    Name = "web"
  }
}

output "rendered_ingress" {
  value = {
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
    from_port = 443
    to_port = 443
  }
}

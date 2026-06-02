terraform {
  required_version = ">= 1.8.0"
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "vpc_id" {
  type = string
}

variable "instance_names" {
  type = list(string)
  default = ["web-a", "web-b"]
}

provider "aws" {
  region = var.region
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners = ["amazon"]
  filter = [{
    name = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }]
}

resource "aws_security_group" "web_security_group" {
  name = "web"
  description = "Web access"
  vpc_id = var.vpc_id

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web_instance" {
  ami = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web_security_group.id]
  tags = {
    Name = "web"
  }
}

resource "aws_instance" "fleet_instance" {
  for_each = toset(var.instance_names)
  ami = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web_security_group.id]
  tags = {
    Name = each.value
  }
}

resource "aws_instance" "fleet_from_python" {
  for_each = [{
    name = "jobs-a"
    instance_type = "t3.micro"
  }, {
    name = "jobs-b"
    instance_type = "t3.small"
  }]
  ami = data.aws_ami.amazon_linux.id
  instance_type = each.value.instance_type
  vpc_security_group_ids = [aws_security_group.web_security_group.id]
  tags = {
    Name = each.value.name
  }
}

output "instance_id" {
  value = aws_instance.web_instance.id
}

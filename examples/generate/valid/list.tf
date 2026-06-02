variable "vpc_id" {
  type = string
}

resource "aws_subnet" "subnet_0" {
  vpc_id = var.vpc_id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "0"
    Label = "subnet_0"
    Order = 0
  }
}

resource "aws_subnet" "subnet_1" {
  vpc_id = var.vpc_id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = {
    Name = "1"
    Label = "subnet_1"
    Order = 1
  }
}

output "subnet_ids" {
  value = [aws_subnet.subnet_0.id, aws_subnet.subnet_1.id]
}

locals {
  label = null
  region = "us-east-1"
}

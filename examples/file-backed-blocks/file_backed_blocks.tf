resource "aws_security_group" "web_security_group" {
  name = "web-dev"
  description = "File-backed web access"
  vpc_id = "vpc-0123456789abcdef0"
  tags = {
    Project = "phcl"
    ManagedBy = "PHCL"
    Environment = "dev"
    Component = "web"
    Name = "web-dev"
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
}

resource "aws_subnet" "public_subnet" {
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  vpc_id = "vpc-0123456789abcdef0"
  tags = {
    Project = "phcl"
    ManagedBy = "PHCL"
    Environment = "dev"
    Component = "web"
    Name = "public-a"
  }
}

output "loaded_config" {
  value = {
    vpc_id = "vpc-0123456789abcdef0"
    security_group_name = "web-dev"
    component = "web"
    network = {
      public = {
        subnet = {
          cidr_block = "10.0.1.0/24"
          availability_zone = "us-east-1a"
        }
      }
    }
  }
}

output "loaded_public_subnet_config" {
  value = {
    cidr_block = "10.0.1.0/24"
    availability_zone = "us-east-1a"
  }
}

output "loaded_tags" {
  value = {
    Project = "phcl"
    ManagedBy = "PHCL"
    Environment = "dev"
    Component = "web"
    Name = "web"
  }
}

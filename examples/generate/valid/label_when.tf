resource "aws_s3_bucket" "app_logs" {
  bucket = "phcl-example-logs"
  tags = {
    Name = "logs"
    ManagedBy = "PHCL"
  }
}

resource "aws_s3_bucket" "app_workload_api" {
  bucket = "phcl-example-api"
  tags = {
    Name = "api"
    Label = "app_workload_api"
    Team = "platform"
    ManagedBy = "PHCL"
  }
}

resource "aws_s3_bucket" "app_workload_web" {
  bucket = "phcl-example-web"
  tags = {
    Name = "web"
    Label = "app_workload_web"
    Team = "frontend"
    ManagedBy = "PHCL"
  }
}

output "example_bucket_ids" {
  value = {
    logs = aws_s3_bucket.app_logs.id
    api = aws_s3_bucket.app_workload_api.id
    web = aws_s3_bucket.app_workload_web.id
  }
}

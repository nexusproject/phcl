resource "aws_s3_bucket" "bucket_logs" {
  force_destroy = true
  bucket = "phcl-example-logs"
  tags = {
    Name = "logs"
    Label = "bucket_logs"
    Purpose = "logs"
    Order = 0
    ManagedBy = "PHCL"
  }
}

resource "aws_s3_bucket" "bucket_assets" {
  force_destroy = true
  bucket = "phcl-example-assets"
  tags = {
    Name = "assets"
    Label = "bucket_assets"
    Purpose = "assets"
    Order = 1
    ManagedBy = "PHCL"
  }
}

output "bucket_ids" {
  value = {
    logs = aws_s3_bucket.bucket_logs.id
    assets = aws_s3_bucket.bucket_assets.id
  }
}

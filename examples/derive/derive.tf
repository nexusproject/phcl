resource "aws_s3_bucket" "logs" {
  force_destroy = true
  tags = {
    ManagedBy = "PHCL"
    Name = "logs"
  }
  bucket = "phcl-example-logs"
}

resource "aws_s3_bucket" "assets" {
  force_destroy = true
  tags = {
    ManagedBy = "PHCL"
    Name = "assets"
  }
  bucket = "phcl-example-assets"
}

resource "aws_s3_bucket" "preview_assets_bucket" {
  force_destroy = true
  tags = {
    ManagedBy = "PHCL"
    Name = "preview-assets"
  }
  bucket = "phcl-example-preview-assets"
}

output "bucket_names" {
  value = {
    logs = aws_s3_bucket.logs.id
    assets = aws_s3_bucket.assets.id
    preview_assets = aws_s3_bucket.preview_assets_bucket.id
  }
}

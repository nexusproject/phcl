resource "aws_s3_bucket" "bucket_logs" {
  for_each = {
    primary = {
      suffix = "primary"
    }
    replica = {
      suffix = "replica"
    }
  }
  bucket = "app-logs"
  tags = {
    Family = "logs"
    Instance = each.value.suffix
  }
}

resource "aws_s3_bucket" "bucket_assets" {
  for_each = {
    primary = {
      suffix = "primary"
    }
    replica = {
      suffix = "replica"
    }
  }
  bucket = "app-assets"
  tags = {
    Family = "assets"
    Instance = each.value.suffix
  }
}

output "primary_bucket_ids" {
  value = {
    logs = aws_s3_bucket.bucket_logs["primary"].id
    assets = aws_s3_bucket.bucket_assets["primary"].id
  }
}

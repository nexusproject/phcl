resource "aws_s3_bucket" "bucket" {
  bucket = "example"
}

resource "aws_s3_bucket" "special_bucket" {
  bucket = "example"
  force_destroy = true
}

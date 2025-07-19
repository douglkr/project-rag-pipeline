resource "aws_s3_bucket" "gen_ai_colpali_bucket" {
  bucket = "name-of-your-bucket"

  tags = {
    Name = "terraform-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "block_public_access" {
  bucket                  = aws_s3_bucket.gen_ai_colpali_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_notification" "eventbridge" {
  bucket = aws_s3_bucket.gen_ai_colpali_bucket.id

  eventbridge = true

  depends_on = [aws_s3_bucket.gen_ai_colpali_bucket]
}

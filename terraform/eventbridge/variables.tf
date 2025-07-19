variable "region" {
  type    = string
  default = "us-east-1"
}

variable "s3_bucket_name" {
  type = string
}

variable "lambda_arn" {
  type = string
}

variable "lambda_name" {
  type = string
}
variable "region" {
  type    = string
  default = "us-east-1"
}

variable "container_image" {
  description = "Docker image to use for ECS task"
  type        = string
}

variable "container_name" {
  description = "Docker name to use for ECS task"
  type        = string
}

variable "s3_bucket_name" {
  type        = string
  description = "The name of the S3 bucket"
}

variable "s3_bucket_arn" {
  type        = string
  description = "The ARN of the S3 bucket"
}
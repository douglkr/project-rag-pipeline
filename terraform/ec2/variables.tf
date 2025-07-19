variable "region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Public subnet ID for EC2"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs to attach to EC2"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for EC2"
  type        = string
}

variable "lambda_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "private_subnet_id" {
  type        = string
  description = "List of private subnet IDs for ECS tasks"
}

variable "security_group_id" {
  type        = string
  description = "List of security group IDs for ECS tasks"
}

variable "ecs_cluster" {
  type        = string
  description = "ECS cluster name"
}

variable "ecs_task_definition" {
  type        = string
  description = "ECS task definition name"
}

variable "ecs_container_name" {
  type        = string
  description = "Docker name to use for ECS task"
}

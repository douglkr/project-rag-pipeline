terraform {
  required_version = "1.12.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.0.0"
    }
  }

  backend "s3" {
    bucket = "your-backend-bucket"
    key    = "your-key.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      owner      = "terraform"
      managed-by = "terraform"
    }
  }
}

module "s3" {
  source = "./s3"
}

module "network" {
  source     = "./network"
  my_ip_cidr = var.my_ip_cidr
}

module "ec2" {
  source             = "./ec2"
  vpc_id             = module.network.vpc_id
  ami_id             = var.ami_id
  instance_type      = var.instance_type
  subnet_id          = module.network.public_subnet_id
  security_group_ids = [module.network.ec2_security_group_id]
}

module "ecr" {
  source = "./ecr"
}

module "ecs" {
  source          = "./ecs"
  container_name  = "your-container-name"
  container_image = "${module.ecr.repository_url}:latest"
  s3_bucket_name  = module.s3.gen_ai_colpali_bucket_name
  s3_bucket_arn   = module.s3.gen_ai_colpali_bucket_arn
}

module "eventbridge" {
  source         = "./eventbridge"
  s3_bucket_name = module.s3.gen_ai_colpali_bucket_name
  lambda_arn     = module.lambda.lambda_arn
  lambda_name    = module.lambda.lambda_name
}

module "lambda" {
  source              = "./lambda"
  lambda_name         = "TriggerEcsOnS3Upload"
  private_subnet_id   = module.network.private_subnet_id
  security_group_id   = module.network.ecs_security_group_id
  ecs_cluster         = module.ecs.ecs_cluster_name
  ecs_task_definition = module.ecs.ecs_task_definition_arn
  ecs_container_name  = module.ecs.ecs_container_name
}

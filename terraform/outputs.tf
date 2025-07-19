output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "private_subnet_id" {
  value = module.network.private_subnet_id
}

output "public_subnet_id" {
  value = module.network.public_subnet_id
}

output "weaviate_security_group_id" {
  value = module.network.ec2_security_group_id
}

output "weaviate_instance_id" {
  value = module.ec2.instance_id
}

output "weaviate_public_ip" {
  value = module.ec2.public_ip
}

output "weaviate_private_ip" {
  value = module.ec2.private_ip
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

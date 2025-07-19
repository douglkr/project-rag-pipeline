output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.vpc.id
}

output "private_subnet_id" {
  value = aws_subnet.private_subnet.id
}

output "public_subnet_id" {
  value = aws_subnet.public_subnet.id
}

output "ec2_security_group_id" {
  value = aws_security_group.ec2_sg.id
}

output "ecs_security_group_id" {
  value = aws_security_group.ecs_sg.id
}

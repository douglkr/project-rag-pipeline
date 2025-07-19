output "instance_id" {
  value = aws_instance.weaviate.id
}

output "public_ip" {
  value = aws_instance.weaviate.public_ip
}

output "private_ip" {
  value = aws_instance.weaviate.private_ip
}

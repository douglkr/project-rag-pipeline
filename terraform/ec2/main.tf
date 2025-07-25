provider "aws" {
  region = var.region
}

resource "aws_key_pair" "key" {
  key_name   = "your-key"
  public_key = file("${path.module}/../key/your-key.pub")
}

resource "aws_instance" "weaviate" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.key.key_name
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = var.security_group_ids
  associate_public_ip_address = true

  tags = {
    Name = "terraform-weaviate-ec2"
  }
}
provider "aws" {
  region = var.region
}

resource "aws_ecr_repository" "colpali_repository" {
  name         = "your-ecr-repository"
  force_delete = true

  tags = {
    Name = "terraform-ecr"
  }
}

provider "aws" {
  region = var.region
}

##########################
# ECS Cluster
##########################
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "gen-ai-colpali-ecs-cluster"

  tags = {
    Name = "terraform-ecs-cluster"
  }
}

##########################
# ECS IAM role
##########################
resource "aws_iam_role" "ecs_task_role" {
  name = "terraform-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "TerraformecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

##########################
# ECS IAM role policy
##########################
resource "aws_iam_role_policy" "s3_read_policy" {
  name = "ecs-task-s3-read"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

##########################
# ECS Log group
##########################

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/colpali-pipeline"
  retention_in_days = 1
}

##########################
# ECS Task definition
##########################
resource "aws_ecs_task_definition" "colpali_pipeline" {
  family                   = "terraform_colpali_pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "4096"  # 4 vCPU
  memory                   = "16384" # 16 GB RAM minimum
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.container_name
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ],
      environment = [
        {
          name  = "S3_BUCKET"
          value = "" # will be overridden at runtime by Lambda
        },
        {
          name  = "S3_KEY"
          value = "" # will be overridden too
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/colpali-pipeline"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  ephemeral_storage {
    size_in_gib = 50
  }
}

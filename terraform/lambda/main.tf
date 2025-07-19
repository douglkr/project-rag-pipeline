data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

##########################
# Lambda IAM role policy
##########################
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Basic execution role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom ECS run permissions
resource "aws_iam_policy" "ecs_run_task" {
  name = "LambdaEcsRunTaskPolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement : [
      {
        Effect = "Allow",
        Action = [
          "ecs:ListTasks",
          "ecs:RunTask",
          "ecs:DescribeClusters",
          "iam:PassRole"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_policy_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.ecs_run_task.arn
}

# Lambda logging (to send logs to CloudWatch)
resource "aws_iam_policy" "lambda_logging" {
  name = "lambda-logging"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logging_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

##########################
# Lambda Log group
##########################

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.trigger_ecs.function_name}"
  retention_in_days = 1

  depends_on = [aws_lambda_function.trigger_ecs]
}

##########################
# Lambda function
##########################
resource "aws_lambda_function" "trigger_ecs" {
  function_name    = var.lambda_name
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  # source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      SUBNET_IDS          = jsonencode([var.private_subnet_id])
      SECURITY_GROUP_IDS  = jsonencode([var.security_group_id])
      ECS_CLUSTER         = var.ecs_cluster
      ECS_TASK_DEFINITION = var.ecs_task_definition
      ECS_CONTAINER_NAME  = var.ecs_container_name
    }
  }
}

output "lambda_arn" {
  value = aws_lambda_function.trigger_ecs.arn
}

output "lambda_name" {
  value = aws_lambda_function.trigger_ecs.function_name
}

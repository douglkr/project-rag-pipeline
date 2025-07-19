provider "aws" {
  region = var.region
}

resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "S3ObjectCreatedRule"
  description = "Trigger Lambda on S3 object upload"
  event_pattern = jsonencode({
    "source"      = ["aws.s3"]
    "detail-type" = ["Object Created"]
    "resources"   = ["arn:aws:s3:::${var.s3_bucket_name}"]
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  target_id = "TriggerLambda"
  arn       = var.lambda_arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_object_created.arn
}

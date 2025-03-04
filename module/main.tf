provider "aws" {
  region = "us-east-1"
}

# Archive a single file.

data "archive_file" "pythonCode" {
  type        = "zip"
  source_file = "${path.module}/python/"
  output_path = "${path.module}/python/lambda_function.zip"
}

# lambda iam role
resource "aws_iam_role" "lambda_role" {
  name               = "lambda-sqs-trigger-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json

  permissions_boundary = aws_iam_policy.permission_boundary.arn
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda-sqs-policy"
  description = "Policy for Lambda function to be triggered by SQS event"
  policy      = data.aws_iam_policy_document.lambda_policy.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions   = ["sqs:CreateQueue", "sqs:ListQueues"]
    resources = ["arn:aws:sqs:*:*:*"]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_policy" "permission_boundary" {
  name        = "lambda-sqs-permission-boundary"
  description = "Permission boundary for Lambda execution"
  policy      = data.aws_iam_policy_document.permission_boundary.json
}

data "aws_iam_policy_document" "permission_boundary" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = ["*"]
  }
}

# Lambda Function to deploy pytho code
resource "aws_lambda_function" "python_lambda" {
  function_name = "sqs-event-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.pythonCode.output_path # Path to your zip file containing Python code

  environment {
    variables = {
      EXAMPLE_VAR = "example"
    }
  }
}

# Creating EventBridge Rule to Trigger Lambda on SQS Queue Creation
resource "aws_cloudwatch_event_rule" "sqs_creation_rule" {
  name        = "sqs-queue-creation-rule"
  description = "Trigger Lambda on SQS queue creation"
  event_pattern = jsonencode({
    source = ["aws.sqs"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventName = ["CreateQueue"]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.sqs_creation_rule.name
  arn       = aws_lambda_function.python_lambda.arn
  input     = jsonencode({ "event" = "queue created" })
}

resource "aws_lambda_permission" "allow_eventbridge_trigger" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.python_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sqs_creation_rule.arn
}

# Outputs
output "lambda_function_name" {
  value = aws_lambda_function.python_lambda.function_name
}

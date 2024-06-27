
resource "aws_lambda_function" "turbot_snow_webhook" {
  function_name    = "turbot_snow_webhook"
  role             = aws_iam_role.lambda_role.arn
  handler          = "function.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  filename         = data.archive_file.lambda_source.output_path
  source_code_hash = data.archive_file.lambda_source.output_base64sha256

  environment {
    variables = {
      AUTH_NAME_SSM_PARAM     = aws_ssm_parameter.authname_param.name
      AUTH_SECRET_SSM_PARAM   = aws_ssm_parameter.authsecret_param.name
      SN_INSTANCE_SSM_PARAM   = aws_ssm_parameter.sn_instance.name
      TURBOT_KEY_SSM_PARAM    = aws_ssm_parameter.turbot-key.name
      TURBOT_SECRET_SSM_PARAM = aws_ssm_parameter.turbot-secret.name
      WORKSPACE_SSM_PARAM     = aws_ssm_parameter.turbot-workspace.name
      VERIFY_CERTIFICATE      = "False"
      POLLING_WINDOW          = 1440
      EXECUTION_MODE          = "RUNNING"
      HTTP_PROXY              = var.HTTP_PROXY
      HTTPS_PROXY             = var.HTTPS_PROXY
      NO_PROXY                = var.NO_PROXY
    }
  }

  vpc_config {
    subnet_ids         = [var.subnet_ids]
    security_group_ids = [var.security_group]
  }

}

resource "aws_lambda_function_event_invoke_config" "example" {
  function_name = aws_lambda_function.turbot_snow_webhook.function_name
  qualifier     = "$LATEST"
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

resource "random_uuid" "lambda_src_hash" {
  keepers = {
    for filename in setunion(
      fileset("${path.cwd}/lambda_function", "function.py"),
      fileset("${path.cwd}/lambda_function", "requirements.txt")
    ):
        filename => filemd5("${path.cwd}/lambda_function/${filename}")
  }
}

data "archive_file" "lambda_source" {
  excludes   = [
    "__pycache__",
    "venv",
  ]

  source_dir  = "${path.cwd}/lambda_function"
  output_path = "${random_uuid.lambda_src_hash.result}.zip"
  type        = "zip"
}

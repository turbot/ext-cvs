
resource "aws_lambda_function" "turbot_snow_webhook" {
  function_name    = "turbot_snow_webhook"
  role             = aws_iam_role.lambda_role.arn
  handler          = "function.lambda_handler"
  runtime          = "python3.12"
  # filename         = "lambda_function.zip"
  # source_code_hash = filebase64sha256("lambda_function.zip")
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
      POLLING_WINDOW          = 10
      HTTP_PROXY              = "http://eastproxies.cvshealth.com:9119"
      HTTPS_PROXY             = "http://eastproxies.cvshealth.com:9119"
      NO_PROXY                = "169.254.169.254,169.254.170.2,localhost"
    }
  }

  vpc_config {
    subnet_ids         = [var.subnet_ids]
    security_group_ids = [var.security_group]
  }

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

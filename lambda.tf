
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
      AUTH_NAME_SSM_PARAM   = aws_ssm_parameter.authname_param.name
      AUTH_SECRET_SSM_PARAM = aws_ssm_parameter.authsecret_param.name
      SN_INSTANCE_SSM_PARAM = aws_ssm_parameter.sn_instance.name
    }
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

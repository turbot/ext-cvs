resource "aws_ssm_parameter" "authname_param" {
  name        = "/turbot/snow-api/authname"
  type        = "SecureString"
}

resource "aws_ssm_parameter" "authsecret_param" {
  name        = "/turbot/snow-api/authsecret"
  type        = "SecureString"
}

resource "aws_ssm_parameter" "turbot-key" {
  name        = "/turbot/snow-api/turbot-key"
  type        = "SecureString"
}

resource "aws_ssm_parameter" "turbot-secret" {
  name        = "/turbot/snow-api/turbot-secret"
  type        = "SecureString"
}

resource "aws_ssm_parameter" "sn_instance" {
  name        = "/turbot/snow-api/sn-instance"
  type        = "String"
  value       = "https://dev12345678.service-now.com"
}

resource "aws_ssm_parameter" "turbot-workspace" {
  name        = "/turbot/snow-api/turbot-workspace"
  type        = "String"
  # value       = "https://demo-turbot.cloud.turbot-dev.com"
  value       = "https://console.turbot-dev.aetna.com"
}

resource "aws_ssm_parameter" "authname_param" {
  name        = "/turbot/snow-api/authname"
  type        = "SecureString"
  value       = "user"
}

resource "aws_ssm_parameter" "authsecret_param" {
  name        = "/turbot/snow-api/authsecret"
  type        = "SecureString"
  value       = "pass"
}

resource "aws_ssm_parameter" "api_token" {
  name        = "/turbot/snow-api/api-token"
  type        = "SecureString"
  value       = "c7594f45-6d92-f29c-eb0e-521490c974f1"
}

resource "aws_ssm_parameter" "sn_instance" {
  name        = "/turbot/snow-api/sn-instance"
  type        = "String"
  value       = "https://dev12345678.service-now.com"
}

resource "aws_ssm_parameter" "turbot-key" {
  name        = "/turbot/snow-api/turbot-key"
  type        = "SecureString"
  value       = "replace"
}

resource "aws_ssm_parameter" "turbot-secret" {
  name        = "/turbot/snow-api/turbot-secret"
  type        = "SecureString"
  value       = "replace"
}

resource "aws_ssm_parameter" "turbot-workspace" {
  name        = "/turbot/snow-api/turbot-workspace"
  type        = "SecureString"
  value       = "https://console.turbot-dev.aetna.com"
}
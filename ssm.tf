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
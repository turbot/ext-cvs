variable "vpc_id" {}
variable "subnet_ids" {}
variable "security_group" {}
variable "aws_profile" {}
variable "aws_region" {}
variable "HTTP_PROXY" {
  default = "http://eastproxies.cvshealth.com:9119"
}
variable "HTTPS_PROXY" {
  default = "http://eastproxies.cvshealth.com:9119"
}
variable "NO_PROXY" {
  default = "169.254.169.254,169.254.170.2,localhost"
}

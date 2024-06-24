provider "aws" {
  region = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      applicationname    = "Turbot"
      costcenter         = "190320"
      dataclassification = "proprietary"
      resourceowner      = "Robert Muturi"
      itpmid             = "78CD82E663CA0E99"
    }
  }
}
provider "aws" {
  version = "3.63.0"
  region  = local.region
  profile = "terraform"
}

data "aws_caller_identity" "this" {}
data "aws_ecr_authorization_token" "token" {}

terraform {
  backend "remote" {
    organization = "linsoft"

    workspaces {
      name = "revlet-propertyservice-deployment"
    }
  }
}

locals {
  region = "eu-west-2"
}
provider "aws" {
  version = "3.63.0"
  region  = "eu-west-2"
  profile = "terraform"
}

terraform {
  backend "remote" {
    organization = "linsoft"

    workspaces {
      name = "linsoft-propertyservice-deployment"
    }
  }
}
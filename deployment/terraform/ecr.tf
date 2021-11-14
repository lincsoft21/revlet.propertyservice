locals {
  ecr_repo = "linsoft.revlet.propertyservice"
}

data "aws_ecr_image" "propertyservice_image" {
  repository_name = local.ecr_repo
  image_tag       = var.IMAGE_TAG
}

data "aws_ecr_repository" "propertyservice_repo" {
  name = local.ecr_repo
}

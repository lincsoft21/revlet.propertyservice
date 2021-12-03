locals {
  propertyservice_handlers = keys(local.function_method_map)
}

resource "aws_lambda_function" "propertyservice_lambda" {
  for_each      = toset(local.propertyservice_handlers)
  function_name = format("propertyservice_%s", each.key)
  role          = aws_iam_role.propertyservice_role.arn
  package_type  = "Image"

  image_uri = format("%s@%s", data.aws_ecr_repository.propertyservice_repo.repository_url, data.aws_ecr_image.propertyservice_image.image_digest)
  image_config {
    command = [format("app.%s", each.key)]
  }

  depends_on = [
    aws_dynamodb_table.propertyservice_table
  ]
}

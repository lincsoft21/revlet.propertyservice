locals {
  propertyservice_handlers = tolist([
    "get_property",
    "post_property"
  ])
}

resource "aws_lambda_function" "propertyservice_lambda" {
  count         = length(local.propertyservice_handlers)
  function_name = format("propertyservice_%s", local.propertyservice_handlers[count.index])
  role          = aws_iam_role.propertyservice_role.arn
  package_type  = "Image"

  image_uri = format("%s@%s", data.aws_ecr_repository.propertyservice_repo.repository_url, data.aws_ecr_image.propertyservice_image.image_digest)
  image_config {
    command = [format("app.%s", local.propertyservice_handlers[count.index])]
  }

  depends_on = [
    aws_dynamodb_table.propertyservice_table
  ]
}

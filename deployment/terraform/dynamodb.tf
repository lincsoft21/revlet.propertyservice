resource "aws_dynamodb_table" "propertyservice_table" {
  name           = format("revlet-%s-properties", var.ENVIRONMENT)
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "propertyId"

  attribute {
    name = "propertyId"
    type = "S"
  }

  tags = {
    env     = var.ENVIRONMENT
    service = "propertyservice"
  }
}

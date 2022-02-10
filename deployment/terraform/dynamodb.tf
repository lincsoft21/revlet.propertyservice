resource "aws_dynamodb_table" "propertyservice_table" {
  name           = format("revlet-propertyservice-%s-db", var.ENVIRONMENT)
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "itemID"
  range_key      = "dataSelector"

  attribute {
    name = "itemID"
    type = "S"
  }

  attribute {
    name = "dataSelector"
    type = "S"
  }

  tags = {
    env     = var.ENVIRONMENT
    service = "propertyservice"
  }
}

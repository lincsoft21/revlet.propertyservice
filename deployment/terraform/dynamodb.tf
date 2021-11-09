resource "aws_dynamodb_table" "propertyservice_table" {
  name           = "linsoft-revelt-properties"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "PropertyId"
  range_key      = "Postcode"

  attribute {
    name = "PropertyId"
    type = "S"
  }

  attribute {
    name = "Postcode"
    type = "S"
  }

  tags = {
    env     = "dev"
    service = "propertyservice"
  }
}
resource "aws_dynamodb_table" "propertyservice_table" {
  name           = "linsoft-revlet-properties"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "PropertyId"

  attribute {
    name = "PropertyId"
    type = "S"
  }

  tags = {
    env     = "dev"
    service = "propertyservice"
  }
}

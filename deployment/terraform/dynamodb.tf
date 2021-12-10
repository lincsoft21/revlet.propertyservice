resource "aws_dynamodb_table" "propertyservice_table" {
  name           = "revlet-properties"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "propertyId"

  attribute {
    name = "propertyId"
    type = "S"
  }

  tags = {
    env     = "dev"
    service = "propertyservice"
  }
}

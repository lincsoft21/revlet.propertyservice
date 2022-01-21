resource "aws_dynamodb_table" "propertyservice_table" {
  name           = format("revlet-%s-properties", var.ENVIRONMENT)
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "propertyId"
  range_key      = "dataSelector"

  attribute {
    name = "propertyId"
    type = "S"
  }

  attribute {
    name = "dataSelector"
    type = "S"
  }

  attribute {
    name = "reviewIndexPK"
    type = "S"
  }

  attribute {
    name = "reviewIndexSK"
    type = "S"
  }

  global_secondary_index {
    name               = "ReviewIndex"
    hash_key           = "reviewIndexPK"
    range_key          = "reviewIndexSK"
    write_capacity     = 20
    read_capacity      = 20
    projection_type    = "INCLUDE"
    non_key_attributes = ["postcode", "streetName"]
  }

  tags = {
    env     = var.ENVIRONMENT
    service = "propertyservice"
  }
}

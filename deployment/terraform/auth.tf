
resource "aws_api_gateway_authorizer" "propertyservice_api_authorizer" {
  name          = "propertyservice-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.propertyservice_api.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = tolist(data.aws_cognito_user_pools.propertyservice_userpool.arns)
  # provider_arns = concat(tolist(data.aws_cognito_user_pools.propertyservice_userpool.arns), tolist(data.aws_cognito_user_pools.propertyservice_admin_userpool.arns))
}

# resource "aws_api_gateway_authorizer" "propertyservice_api_admin_authorizer" {
#   name          = "propertyservice-admin-authorizer"
#   rest_api_id   = aws_api_gateway_rest_api.propertyservice_api.id
#   type          = "COGNITO_USER_POOLS"
#   provider_arns = data.aws_cognito_user_pools.propertyservice_admin_userpool.arns
# }

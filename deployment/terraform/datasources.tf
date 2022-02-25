data "aws_cognito_user_pools" "propertyservice_userpool" {
  name = format("revlet-%s-userpool", var.ENVIRONMENT)
}

# data "aws_cognito_user_pools" "propertyservice_admin_userpool" {
#   name = format("revlet-%s-admin-userpool", var.ENVIRONMENT)
# }

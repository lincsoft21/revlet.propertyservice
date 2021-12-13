locals {
  function_method_map = {
    get_properties = {
      method    = "GET"
      model     = null
      validator = null
      params = {
        "method" = {
          "method.request.querystring.id" = false
        },
        "template" = {
          "application/json" = jsonencode({
            "id" = "$input.params('id')"
          })
        }
      }
    }
    post_property = {
      method = "POST"
      model = {
        "application/json" = aws_api_gateway_model.propertyservice_model.name
      }
      validator = aws_api_gateway_request_validator.propertyservice_model_validator.id
      params = {
        "method"   = null,
        "template" = null
      }
    }
    update_property_details = {
      method = "PUT"
      model = {
        "application/json" = aws_api_gateway_model.propertyservice_details_model.name
      }
      validator = aws_api_gateway_request_validator.propertyservice_model_validator.id
      params = {
        "method" = {
          "method.request.querystring.id" = false
        },
        "template" = {
          "application/json" = jsonencode({
            "id" = "$input.params('id')"
          })
        }
      }
    }
    delete_property = {
      method    = "DELETE"
      model     = null
      validator = null
      params = {
        "method" = {
          "method.request.querystring.id" = true
        },
        "template" = {
          "application/json" = jsonencode({
            "id" = "$input.params('id')"
          })
        }
      }
    }
  }
}

resource "aws_api_gateway_rest_api" "propertyservice_api" {
  name = "propertyservice_api"
}

resource "aws_api_gateway_resource" "propertyservice_gateway_properties_resource" {
  path_part   = "properties"
  parent_id   = aws_api_gateway_rest_api.propertyservice_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
}

resource "aws_api_gateway_method" "propertyservice_method" {
  for_each      = local.function_method_map
  rest_api_id   = aws_api_gateway_rest_api.propertyservice_api.id
  resource_id   = aws_api_gateway_resource.propertyservice_gateway_properties_resource.id
  http_method   = each.value.method
  authorization = "NONE"

  request_parameters   = each.value.params.method
  request_validator_id = each.value.validator
  request_models       = each.value.model
}

resource "aws_api_gateway_integration" "propertyservice_lambda_integration" {
  for_each                = local.function_method_map
  rest_api_id             = aws_api_gateway_rest_api.propertyservice_api.id
  resource_id             = aws_api_gateway_resource.propertyservice_gateway_properties_resource.id
  http_method             = aws_api_gateway_method.propertyservice_method[each.key].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.propertyservice_lambda[each.key].invoke_arn
  passthrough_behavior    = "WHEN_NO_TEMPLATES"

  request_templates = each.value.params.template
}

resource "aws_lambda_permission" "propertyservice_lambda_permission" {
  for_each      = local.function_method_map
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.propertyservice_lambda[each.key].function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = format("arn:aws:execute-api:%s:%s:%s/*/%s%s", local.region, data.aws_caller_identity.this.account_id, aws_api_gateway_rest_api.propertyservice_api.id, aws_api_gateway_method.propertyservice_method[each.key].http_method, aws_api_gateway_resource.propertyservice_gateway_properties_resource.path)
}


resource "aws_api_gateway_request_validator" "propertyservice_model_validator" {
  name                        = "propertyservice_validator"
  rest_api_id                 = aws_api_gateway_rest_api.propertyservice_api.id
  validate_request_body       = true
  validate_request_parameters = false
}

resource "aws_api_gateway_model" "propertyservice_model" {
  rest_api_id  = aws_api_gateway_rest_api.propertyservice_api.id
  name         = "Property"
  description  = "Property API Input Model"
  content_type = "application/json"

  schema = file("${path.module}/models/property.json")
}

resource "aws_api_gateway_model" "propertyservice_details_model" {
  rest_api_id  = aws_api_gateway_rest_api.propertyservice_api.id
  name         = "PropertyDetails"
  description  = "Property API Details Model"
  content_type = "application/json"

  schema = file("${path.module}/models/property_details.json")
}

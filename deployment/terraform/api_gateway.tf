locals {
  resources = ["properties", "reviews"]
  models    = ["property", "review", "PropertyDetails"]
  function_method_map = {
    get_properties = {
      method     = "GET"
      resource   = "properties"
      model      = null
      validator  = null
      authorizer = null
      params = {
        "method" = {
          "method.request.querystring.p"  = false
          "method.request.querystring.id" = false
        },
        "template" = {
          "application/json" = jsonencode({
            "p"  = "$input.params('p')",
            "id" = "$input.params('id')"
          })
        }
      }
    }
    post_property = {
      method   = "POST"
      resource = "properties"
      model = {
        "application/json" = aws_api_gateway_model.propertyservice_models["property"].name
      }
      validator  = aws_api_gateway_request_validator.propertyservice_model_validator.id
      authorizer = aws_api_gateway_authorizer.propertyservice_api_authorizer.id
      params = {
        "method"   = null,
        "template" = null
      }
    }
    update_property_details = {
      method   = "PUT"
      resource = "properties"
      model = {
        "application/json" = aws_api_gateway_model.propertyservice_models["PropertyDetails"].name
      }
      validator  = aws_api_gateway_request_validator.propertyservice_model_validator.id
      authorizer = aws_api_gateway_authorizer.propertyservice_api_authorizer.id
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
      method     = "DELETE"
      resource   = "properties"
      model      = null
      validator  = null
      authorizer = aws_api_gateway_authorizer.propertyservice_api_admin_authorizer.id
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
    get_reviews = {
      method     = "GET"
      resource   = "reviews"
      model      = null
      validator  = null
      authorizer = null
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
    post_review = {
      method   = "POST"
      resource = "reviews"
      model = {
        "application/json" = aws_api_gateway_model.propertyservice_models["review"].name
      }
      validator  = aws_api_gateway_request_validator.propertyservice_model_validator.id
      authorizer = aws_api_gateway_authorizer.propertyservice_api_authorizer.id
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
    delete_review = {
      method     = "DELETE"
      resource   = "reviews"
      model      = null
      validator  = aws_api_gateway_request_validator.propertyservice_model_validator.id
      authorizer = aws_api_gateway_authorizer.propertyservice_api_authorizer.id
      params = {
        "method" = {
          "method.request.querystring.id" = true
          "method.request.querystring.r"  = true
        },
        "template" = {
          "application/json" = jsonencode({
            "id" = "$input.params('id')",
            "r"  = "$input.params('r')"
          })
        }
      }
    }
  }
}

resource "aws_api_gateway_rest_api" "propertyservice_api" {
  name = format("propertyservice-%s-api", var.ENVIRONMENT)
}

resource "aws_api_gateway_resource" "propertyservice_gateway_properties_resource" {
  for_each    = toset(local.resources)
  path_part   = each.value
  parent_id   = aws_api_gateway_rest_api.propertyservice_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
}

# resource "aws_api_gateway_resource" "propertyservice_gateway_test_property_resources" {
#   count    = length(local.property_resources)
#   path_part   = local.property_resources[count.index]
#   parent_id   = count.index == 0 ? aws_api_gateway_rest_api.propertyservice_api.root_resource_id : element(aws_api_gateway_resource.propertyservice_gateway_test_property_resources.*.id, count.index - 1)
#   rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
# }

resource "aws_api_gateway_resource" "propertyservice_gateway_property_id_resource" {
  path_part = "{id}"
  parent_id = aws_api_gateway_resource.propertyservice_gateway_properties_resource["properties"].id
  rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
}

resource "aws_api_gateway_method" "test_method" {
  rest_api_id      = aws_api_gateway_rest_api.propertyservice_api.id
  resource_id      = aws_api_gateway_resource.propertyservice_gateway_property_id_resource.id
  http_method      = "GET"

  authorization = "NONE"

  request_parameters = {
    "method.request.path.id" = true
  }
}

resource "aws_api_gateway_resource" "propertyservice_gateway_review_resource" {
  path_part = "reviews"
  parent_id = aws_api_gateway_resource.propertyservice_gateway_property_id_resource.id
  rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
}

resource "aws_api_gateway_resource" "propertyservice_gateway_review_id_resource" {
  path_part = "{reviewId}"
  parent_id = aws_api_gateway_resource.propertyservice_gateway_properties_resource["reviews"].id
  rest_api_id = aws_api_gateway_rest_api.propertyservice_api.id
}

resource "aws_api_gateway_method" "propertyservice_method" {
  for_each         = local.function_method_map
  rest_api_id      = aws_api_gateway_rest_api.propertyservice_api.id
  resource_id      = aws_api_gateway_resource.propertyservice_gateway_properties_resource[each.value.resource].id
  http_method      = each.value.method
  api_key_required = true

  authorization = each.value.method == "GET" ? "NONE" : "COGNITO_USER_POOLS"
  authorizer_id = each.value.authorizer

  request_parameters   = each.value.params.method
  request_validator_id = each.value.validator
  request_models       = each.value.model
}

resource "aws_api_gateway_integration" "propertyservice_lambda_integration" {
  for_each                = local.function_method_map
  rest_api_id             = aws_api_gateway_rest_api.propertyservice_api.id
  resource_id             = aws_api_gateway_resource.propertyservice_gateway_properties_resource[each.value.resource].id
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
  source_arn = format("arn:aws:execute-api:%s:%s:%s/*/%s%s", local.region, data.aws_caller_identity.this.account_id, aws_api_gateway_rest_api.propertyservice_api.id, aws_api_gateway_method.propertyservice_method[each.key].http_method, aws_api_gateway_resource.propertyservice_gateway_properties_resource[each.value.resource].path)
}


resource "aws_api_gateway_request_validator" "propertyservice_model_validator" {
  name                        = "propertyservice-validator"
  rest_api_id                 = aws_api_gateway_rest_api.propertyservice_api.id
  validate_request_body       = true
  validate_request_parameters = false
}


resource "aws_api_gateway_model" "propertyservice_models" {
  for_each     = toset(local.models)
  rest_api_id  = aws_api_gateway_rest_api.propertyservice_api.id
  name         = each.value
  description  = format("%s model", each.value)
  content_type = "application/json"

  schema = file("${path.module}/models/${each.value}.json")
}

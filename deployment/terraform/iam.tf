resource "aws_iam_role" "propertyservice_role" {
  name = "propertyservice-role"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  tags = {
    env     = "dev"
    service = "propertyservice"
  }
}

resource "aws_iam_role_policy" "dynamodb_policy" {
  name = "propertyservice_policy"
  role = aws_iam_role.propertyservice_role.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:BatchGet*",
          "dynamodb:DescribeStream",
          "dynamodb:Get*",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:Delete*",
          "dynamodb:Update*",
          "dynamodb:PutItem"
        ],
        "Resource" : format("arn:aws:dynamodb:eu-west-2:%s:table/%s", var.AWS_ACCOUNT_ID, aws_dynamodb_table.propertyservice_table.name)
      }
  ] })
}

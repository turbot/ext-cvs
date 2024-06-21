# resource "aws_api_gateway_rest_api" "turbot_snow_webhook" {
#   name        = "turbot_snow_webhook"
#   description = "Webhook for Turbot to Service Now integration"
# }

# resource "aws_api_gateway_resource" "task_resource" {
#   rest_api_id = aws_api_gateway_rest_api.turbot_snow_webhook.id
#   parent_id   = aws_api_gateway_rest_api.turbot_snow_webhook.root_resource_id
#   path_part   = "task"
# }

# resource "aws_api_gateway_method" "post_task" {
#   rest_api_id   = aws_api_gateway_rest_api.turbot_snow_webhook.id
#   resource_id   = aws_api_gateway_resource.task_resource.id
#   http_method   = "POST"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "task_integration" {
#   rest_api_id             = aws_api_gateway_rest_api.turbot_snow_webhook.id
#   resource_id             = aws_api_gateway_resource.task_resource.id
#   http_method             = aws_api_gateway_method.post_task.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.lambda_function.invoke_arn
# }

# resource "aws_api_gateway_deployment" "task_deployment" {
#   rest_api_id = aws_api_gateway_rest_api.turbot_snow_webhook.id

#   triggers = {
#     redeployment = sha1(jsonencode([
#       aws_api_gateway_resource.task_resource.id,
#       aws_api_gateway_method.post_task.id,
#       aws_api_gateway_integration.task_integration.id,
#     ]))
#   }

#   lifecycle {
#     create_before_destroy = true
#   }
# }

# resource "aws_api_gateway_stage" "development" {
#   deployment_id = aws_api_gateway_deployment.task_deployment.id
#   rest_api_id   = aws_api_gateway_rest_api.turbot_snow_webhook.id
#   stage_name    = "development"
# }

# resource "aws_api_gateway_model" "taskModel" {
#   rest_api_id  = aws_api_gateway_rest_api.turbot_snow_webhook.id
#   name         = "task"
#   description  = "a JSON schema"
#   content_type = "application/json"

#   schema = jsonencode({
#     type = "object"
#   })
# }


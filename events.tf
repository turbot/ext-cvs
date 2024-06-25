
resource "aws_cloudwatch_event_rule" "snow_integration_tick" {
    name = "snow_integration_tick"
    description = "Fires every five minutes"
    schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "snow_integration_target" {
    rule = aws_cloudwatch_event_rule.snow_integration_tick.name
    target_id = "snow_integration_target"
    arn = aws_lambda_function.turbot_snow_webhook.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_lambda" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.turbot_snow_webhook.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.snow_integration_tick.arn
}
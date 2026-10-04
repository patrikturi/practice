output "http_api_endpoint" {
  value = aws_apigatewayv2_stage.http.invoke_url
}

output "http_api_id" {
  value = aws_apigatewayv2_api.http.id
}

output "websocket_api_endpoint" {
  value = aws_apigatewayv2_stage.ws.invoke_url
}

output "websocket_api_id" {
  value = aws_apigatewayv2_api.ws.id
}

output "websocket_management_endpoint" {
  value = "https://${aws_apigatewayv2_api.ws.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.stage_name}"
}

output "waf_acl_arn" {
  value = aws_wafv2_web_acl.main.arn
}

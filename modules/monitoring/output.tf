output "sns_topic_arn" {
  description = "생성된 SNS 토픽의 ARN"
  value       = aws_sns_topic.alerts.arn
}
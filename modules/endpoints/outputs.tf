output "ssm_endpoint_ids" {
  value = { for k, v in aws_vpc_endpoint.ssm : k => v.id }
}

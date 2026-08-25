output "vpce_security_group_id" {
  value = aws_security_group.vpce.id
}

output "ssm_endpoint_ids" {
  value = { for k, v in aws_vpc_endpoint.ssm : k => v.id }
}

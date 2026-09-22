output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  value = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  value = aws_subnet.private_db[*].id
}

# EKS 노드가 이 RT(NAT egress) 완료 전에 뜨지 않도록 의존성 고리에 사용
output "private_route_table_id" {
  value = aws_route_table.private.id
}

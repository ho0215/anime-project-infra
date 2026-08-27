output "alb_sg_id" {
  value = aws_security_group.alb.id
}

output "app_sg_id" {
  value = aws_security_group.app.id
}

output "db_sg_id" {
  value = aws_security_group.db.id
}

output "redis_sg_id" {
  value = aws_security_group.redis.id
}

output "efs_sg_id" {
  value = aws_security_group.efs.id
}

output "nat_sg_id" {
  value = aws_security_group.nat.id
}

output "bastion_sg_id" {
  value = aws_security_group.bastion.id
}

output "vpce_sg_id" {
  value = aws_security_group.vpce.id
}
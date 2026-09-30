output "redis_endpoint" {
  description = "REDIS_URL 조립용 (redis://<endpoint>:<port>/0)"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  value = aws_elasticache_cluster.redis.port
}

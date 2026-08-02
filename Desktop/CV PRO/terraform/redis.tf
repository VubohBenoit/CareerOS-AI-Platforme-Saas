# Redis cluster for caching

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "careerosai-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  tags = {
    Name = "careerosai-redis"
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "careerosai-redis-subnet"
  subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]
}

resource "aws_security_group" "redis" {
  name        = "careerosai-redis"
  description = "Redis security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

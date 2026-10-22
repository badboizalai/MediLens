output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "app_subnet_ids" {
  value = aws_subnet.app[*].id
}

output "worker_subnet_ids" {
  description = "Isolated subnets: no internet route."
  value       = aws_subnet.worker[*].id
}

output "app_security_group_id" {
  value = aws_security_group.app.id
}

output "worker_security_group_id" {
  value = aws_security_group.worker.id
}

output "vpce_security_group_id" {
  value = aws_security_group.vpce.id
}

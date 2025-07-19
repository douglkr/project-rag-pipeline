output "ecs_cluster_name" {
  value = aws_ecs_cluster.ecs_cluster.name
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.colpali_pipeline.arn
}

output "ecs_container_name" {
  value = var.container_name
}

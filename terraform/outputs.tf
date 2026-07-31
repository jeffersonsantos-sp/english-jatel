output "resource_group_name" {
  description = "Nome do Resource Group"
  value       = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  description = "Nome do cluster AKS"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "aks_cluster_fqdn" {
  description = "FQDN do cluster AKS"
  value       = azurerm_kubernetes_cluster.aks.fqdn
}

output "kube_config_command" {
  description = "Comando para configurar kubectl"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_kubernetes_cluster.aks.name}"
}

output "dns_zone_name_servers" {
  description = "Name servers do DNS Zone (configurar no registrador)"
  value       = azurerm_dns_zone.main.name_servers
}

output "public_ip_address" {
  description = "IP público do Ingress"
  value       = azurerm_public_ip.ingress.ip_address
}

output "ingress_url" {
  description = "URL do app"
  value       = "https://${var.subdomain}.${var.domain_name}"
}

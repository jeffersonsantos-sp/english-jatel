resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.dns_prefix
  kubernetes_version = null

  default_node_pool {
    name                = "default"
    vm_size             = var.vm_size
    os_disk_size_gb     = var.os_disk_size_gb
    enable_auto_scaling = true
    node_count          = var.node_count
    min_count           = var.min_node_count
    max_count           = var.max_node_count
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "kubenet"
    network_policy = "calico"
  }

  oidc_issuer_enabled = true

  tags = var.tags
}

resource "azurerm_dns_zone" "main" {
  name                = var.domain_name
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

resource "azurerm_dns_zone" "britlearn" {
  name                = "britlearnacademy.online"
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

resource "azurerm_public_ip" "ingress" {
  name                = "pip-ingress-jatel-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "jatel-${random_string.suffix.result}"
  tags                = var.tags
}

resource "azurerm_role_assignment" "aks_network_contributor" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "Network Contributor"
  scope                = azurerm_resource_group.main.id
}

resource "azurerm_role_assignment" "aks_dns_contributor" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "DNS Zone Contributor"
  scope                = azurerm_dns_zone.main.id
}

resource "azurerm_role_assignment" "aks_britlearn_dns_contributor" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "DNS Zone Contributor"
  scope                = azurerm_dns_zone.britlearn.id
}

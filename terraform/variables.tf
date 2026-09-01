variable "subscription_id" {
  description = "ID da subscription Azure"
  type        = string
}

variable "resource_group_name" {
  description = "Nome do Resource Group"
  type        = string
  default     = "rg-english-jatel"
}

variable "location" {
  description = "Região Azure"
  type        = string
  default     = "centralindia"
}

variable "cluster_name" {
  description = "Nome do cluster AKS"
  type        = string
  default     = "aks-english-jatel"
}

variable "dns_prefix" {
  description = "Prefixo DNS do cluster"
  type        = string
  default     = "englishjatel"
}

variable "kubernetes_version" {
  description = "Versão do Kubernetes"
  type        = string
  default     = "1.29"
}

variable "vm_size" {
  description = "Tamanho da VM do node pool"
  type        = string
  default     = "Standard_B2als_v2"
}

variable "node_count" {
  description = "Número de nodes"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Número máximo de nodes (auto-scaler)"
  type        = number
  default     = 2
}

variable "min_node_count" {
  description = "Número mínimo de nodes (auto-scaler)"
  type        = number
  default     = 1
}

variable "os_disk_size_gb" {
  description = "Tamanho do disco OS (GB)"
  type        = number
  default     = 30
}

variable "domain_name" {
  description = "Nome do domínio"
  type        = string
  default     = "jfs-devops.shop"
}

variable "subdomain" {
  description = "Subdomínio do app"
  type        = string
  default     = "learn"
}

variable "tags" {
  description = "Tags para os recursos"
  type        = map(string)
  default = {
    Environment = "dev"
    Project     = "english-jatel"
    ManagedBy   = "terraform"
  }
}

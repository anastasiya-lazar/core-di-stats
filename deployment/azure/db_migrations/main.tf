locals {
  name = "${var.env_prefix}-${var.name}"
}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
  }

  backend "azurerm" {
    resource_group_name  = "RnD"
    storage_account_name = "fkgbstdevops"
    container_name       = "tfstate"
    key                  = "terraform-stats-di-db-migrations.tfstate"
  }


  required_version = ">= 0.14.9"
}

provider kubernetes {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    #    Temp solution to use local configs
    config_path = "~/.kube/config"
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

########################################################################################################################
## Read specific DB secret #############################################################################################
########################################################################################################################

data "azurerm_key_vault" "db_secret" {
  name                = var.vault_name
  resource_group_name = var.vault_resource_group
}

data "azurerm_key_vault_secret" "host_name" {
  name         = var.db_host_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}
data "azurerm_key_vault_secret" "db_username" {
  name         = var.db_username_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_user_pass" {
  name         = var.db_user_pass_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_ssl_path_cert" {
  name         = var.db_ssl_path_cert_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}
data "azurerm_key_vault_secret" "db_name" {
  name         = var.dev_db_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}
data "azurerm_key_vault_secret" "db_ssl_enabled" {
  name         = var.dev_db_ssl_enabled
  key_vault_id = data.azurerm_key_vault.db_secret.id
}
########################################################################################################################
## Save DB info in Vault ###############################################################################################
########################################################################################################################
resource "azurerm_key_vault" "output_db_info" {
  name                = var.output_vault_name
  resource_group_name = var.vault_resource_group
  location            = var.location
  sku_name            = "standard"
  tenant_id           = data.azurerm_client_config.current.tenant_id

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = var.owner
    secret_permissions = ["set", "get", "delete", "purge", "recover", "list"]
  }
}
resource "azurerm_key_vault_secret" "output_db_type" {
  name         = var.output_db_type_name
  value        = var.db_type
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_name" {
  name         = var.dev_db_name
  value        = data.azurerm_key_vault_secret.db_name.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_host" {
  name         = var.db_host_name
  value        = data.azurerm_key_vault_secret.host_name.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_user" {
  name         = var.db_username_name
  value        = data.azurerm_key_vault_secret.db_username.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_pass" {
  name         = var.db_user_pass_name
  value        = data.azurerm_key_vault_secret.db_user_pass.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_ssl_path_cert" {
  name         = var.db_ssl_path_cert_name
  value        = data.azurerm_key_vault_secret.db_ssl_path_cert.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}
resource "azurerm_key_vault_secret" "output_db_ssl_enabled" {
  name         = var.dev_db_ssl_enabled
  value        = data.azurerm_key_vault_secret.db_ssl_enabled.value
  key_vault_id = azurerm_key_vault.output_db_info.id
}

########################################################################################################################
## Migration job #######################################################################################################
########################################################################################################################

resource "helm_release" "stats_db_migration_job" {
  name  = local.name
  chart = "./chart"

  set {
    name  = "container.image"
    value = var.db_migration_docker_image
  }

  set {
    name  = "db_type"
    value = var.db_type
  }

  set {
    name  = "db_endpoint"
    value = data.azurerm_key_vault_secret.host_name.value
  }

  set {
    name  = "db_name"
    value = data.azurerm_key_vault_secret.db_name.value
  }
  set {
    name  = "db_username"
    value = data.azurerm_key_vault_secret.db_username.value
  }
  set {
    name  = "db_password"
    value = data.azurerm_key_vault_secret.db_user_pass.value
  }
  set {
      name  = "db_ssl_path_cert"
      value = data.azurerm_key_vault_secret.db_ssl_path_cert.value
  }
  set {
      name  = "db_ssl_enabled"
      value = data.azurerm_key_vault_secret.db_ssl_enabled.value
  }
}

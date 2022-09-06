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
    key                  = "terraform-di-stats-handler.tfstate"
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


data "azurerm_key_vault" "db_secret" {
  name                = var.db_vault_name
  resource_group_name = var.vault_resource_group
}

data "azurerm_key_vault_secret" "db_type" {
  name         = var.db_type_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_host" {
  name         = var.db_host_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_name" {
  name         = var.db_name_secret
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_user" {
  name         = var.db_username_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_password" {
  name         = var.db_user_pass_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

data "azurerm_key_vault_secret" "db_ssl_path_cert" {
  name         = var.db_ssl_path_cert_name
  key_vault_id = data.azurerm_key_vault.db_secret.id
}

resource "helm_release" "stats_handler" {
  name  = local.name
  chart = "${path.module}/chart"

  set {
    name  = "name"
    value = local.name
  }

  set {
    name  = "container.image"
    value = var.service_image
  }

  set {
    name  = "db_type"
    value = data.azurerm_key_vault_secret.db_type.value
  }

  set {
    name  = "db_endpoint"
    value = data.azurerm_key_vault_secret.db_host.value
  }

  set {
    name  = "db_name"
    value = data.azurerm_key_vault_secret.db_name.value
  }

  set {
    name  = "db_username"
    value = data.azurerm_key_vault_secret.db_user.value
  }

  set {
    name  = "db_password"
    value = data.azurerm_key_vault_secret.db_password.value
  }

  set {
    name  = "db_ssl_path_cert"
    value = data.azurerm_key_vault_secret.db_ssl_path_cert.value
  }
}
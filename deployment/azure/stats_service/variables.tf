variable "name" {
  description = "Name of the service, which is deployed (i.e. stats-handler)"
  default = "stats-worker"
}

variable "env_prefix" {
  description = "prefix of the environment"
  default = "core-di-dev"
}

variable "service_image" {
  description = "name of the image with migration"
}

variable "vault_resource_group" {
  description = "Resource group of the vault"
  default = "RnD"
}

variable "db_vault_name" {
  description = "Name of the vault"
  default = "di-dev-stats-db-info"
}

variable "db_type_name" {
  description = "DB Type: mysql, mariadb etc."
  default = "dev-db-type"
}

variable "db_host_name" {
  description = "Host of DB"
  default = "dev-db-host"
}

variable "db_name_secret" {
  description = "DB name"
  default = "dev-db-name"
}

variable "db_username_name" {
  description = "User of DB"
  default = "dev-db-username"
}

variable "db_user_pass_name" {
  description = "User pass of DB"
  default = "dev-db-user-pass"
}

variable "db_ssl_path_cert_name" {
  default = "dev-ssl-path"
}
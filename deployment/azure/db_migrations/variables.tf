variable "output_db_type_name" {
  description = "DB Type: mysql, mariadb etc."
  default = "dev-db-type"
}
variable "db_type" {
  description = "MYSQL or MARIADB"
}
variable "db_migration_docker_image" {
  description = "name of the image with migration"
}
##############################################################################################
variable "env_prefix" {
  description = "prefix of the environment"
  default = "core-di-dev"
}
variable "name" {
  description = "Name of the service, which is deployed (i.e. stats-handler)"
  default = "stats-db-migration-job"
}

##############################################################################################
variable "vault_name" {
  description = "Name of the vault"
}
variable "vault_resource_group" {
  description = "Resource group of the vault"
  default = "RnD"
}
variable "location" {
  description = "location of the resource group"
  default = "West Europe"
}
variable "owner" {
  description = "ID of the owner (user id, group id, etc)"
  default     = "1b2c20ba-156c-4b87-9f38-d2699541ddbc"
}
################################################################################
variable "db_host_name" {
  description = "Host of DB"
  default = "dev-db-host"
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
  description = "path to the cert file"
  default = "dev-ssl-path"
}

################################################################################
variable "output_vault_name" {
  default = "di-dev-stats-db-info"
}
variable "dev_db_name" {
  description = "DB name"
  default = "dev-db-name"
}
variable "dev_db_ssl_enabled" {
  description = "DB ssl enabled"
  default = "dev-db-ssl-enabled"
}
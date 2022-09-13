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


########################################################################################

variable "authenticator_url" {
  default = "http://20.79.67.241/v1/generic_auth_jwt_verifier"
}

variable "dns_name" {
  default = "stats-di.toronto-poc.xara.ai"
}

variable "port" {
  description = "Port of the service"
  default = "6786"
}

variable "kg_vault_endpoint_key_name" {
  default = "dev-stats-di"
}

variable "maintainer_team" {
  default = "Core-Quantum"
}

variable "maintainer_contact" {
  default = "mihail.beliy@blackswan-technologies.com"
}

variable "di_stats_auth_vault_name" {
  default = "di-stats-auth"
}

variable "di_stats_auth_vault_client_id_key" {
  default = "azure-client-id"
}
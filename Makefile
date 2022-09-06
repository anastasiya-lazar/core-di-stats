# Load .env
ifneq ("$(wildcard .env)","")
    include .env
    export $(shell sed 's/=.*//' .env)
else
endif

WORKDIR := $(shell pwd)
.ONESHELL:
.EXPORT_ALL_VARIABLES:
DOCKER_BUILDKIT=1

ENV_FILE?=$(WORKDIR)/.env
include $(ENV_FILE)
export $(cut -d= -f1 $(ENV_FILE) | grep -v -e "#")

HELM_EXPERIMENTAL_OCI=1

VERSION?=0.0.1_build$(shell date +%s )
NAME?=core-di-gen1-stats-handler

# Azure deployment
CLUSTER?=toronto-backend-cluster
AZ_AKS_REPO_NAME?=akstoronto
AKS_REPO?=$(AZ_AKS_REPO_NAME).azurecr.io
AZURE_REGESTRY_IMAGE_NAME?=$(AKS_REPO)/$(NAME)
AZURE_REGESTRY_MIGRATION_IMAGE_NAME?=$(AKS_REPO)/$(NAME)-migration
AZURE_REGESTRY_TAG?=$(VERSION)

DB_MIGRATION_ARTIFACT_INFO?=$(WORKDIR)/.build/db_migration_artifact_info
AZ_IMAGE_ARTIFACT_INFO?=$(WORKDIR)/.build/az_image_artifact_info

ifeq ($(DB_TYPE), MARIADB)
DB_MIGRATION_TARGET?=mariadb_migration
DB_VAULT?=di-stats-dev-db-mariadb
else ifeq ($(DB_TYPE), MYSQL)
DB_MIGRATION_TARGET?=mysql_migration
DB_VAULT?=di-stats-dev-db-mysql
else
$(info DB_TYPE is not set!)
endif

__CHECK:=$(shell \
	mkdir -p $(WORKDIR)/.build; \
  	if test -f .env; then \
		printf 'Current env: %s\n\n' "$$(readlink .env)" >&2; \
	else \
	  printf '\033[31m%s\033[0m\n\n' "WARNING: ENV NOT SELECTED" >&2; \
	fi; \
)


help: ## Display help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'
	@echo "\nHere used env, which is set by ENV_FILE( ${ENV_FILE} ). To change it, please use "

git_hooks_init: ##Setup git hooks
	@$(WORKDIR)/helper_scripts/init.sh
	@echo "Git hooks setuped"

show_env_setting: ## Print env settings, which will be used for the container run
	@echo "Setting file::\t $(ENV_FILE)\n\n"
	@cat $(ENV_FILE)

list_envs: ## List of the predefined environments, in the ./envs dir
	@ls $(WORKDIR)/envs/ |  grep -v -e "example.env" | grep -v -e "readme.md" > $(WORKDIR)/.build/envs
	@printf "%-7s \033[36m%s\033[0m\n" "Env ID" "Env Name";
	@number=1; while  read -r line; do \
  		printf "   %-4s \033[36m%s\033[0m\n" $$number $$line; \
  		number=$$(( $$number +1 )); \
	done < $(WORKDIR)/.build/envs

set_default_env: list_envs ## Switch current default env (used, if ENV_FILE not set)
	@echo "Please select envID ot paste path to the file" ;\
	read EnvName ;\
	if test -f "$$EnvName"; then \
		echo "$$EnvName exists."; \
	else \
	  selectedEnv=$$(awk "NR==$$EnvName"  $(WORKDIR)/.build/envs);\
	  echo "Selected env: $$selectedEnv ($(WORKDIR)/envs/$$selectedEnv)"; \
	  ln -sf  $(WORKDIR)/envs/$$selectedEnv $(WORKDIR)/.env ;\
	fi

compose_up: ## Start services
	if [ "$(DB_TYPE)" = "MYSQL" ]; then \
		docker-compose --profile mysql up --build; \
	elif [ "$(DB_TYPE)" = "MARIADB" ]; then \
	    docker-compose --profile mariadb up --build; \
	else echo "No DB_TYPE env set"; \
	fi

create_migrations_mariadb:
	docker-compose --profile mariadb up -d;
	docker-compose run core-di-stats-handler-gen1 bash -c "cd solution/sp/sql_base/mariadb/ && alembic revision --autogenerate"
	docker-compose down
	echo "Add newly created migrations to the repository: git add new_files..."

create_migrations_mysql:
	docker-compose --profile mysql up -d;
	docker-compose run core-di-stats-handler-gen1 bash -c "cd solution/sp/sql_base/mysql/ && alembic revision --autogenerate"
	docker-compose down
	echo "Add newly created migrations to the repository: git add new_files..."

aks_login: ## Log in AKS Repo
	az acr login --name $(AZ_AKS_REPO_NAME)

build_stats_db_migration_image: ## build image for apply db migrations
	docker build \
		--target $(DB_MIGRATION_TARGET) \
		--build-arg PIP_EXTRA_INDEX_URL=$(PIP_EXTRA_INDEX_URL) \
		-t $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):latest \
		-f $(WORKDIR)/Dockerfile $(WORKDIR) ;
	docker tag $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):latest $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	docker push   $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):latest
	docker push   $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	echo $(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	echo "$(AZURE_REGESTRY_MIGRATION_IMAGE_NAME):$(AZURE_REGESTRY_TAG)" > $(DB_MIGRATION_ARTIFACT_INFO)

deploy_db_migrations: ## Deploy stats db and apply migrations
	cd $(WORKDIR)/deployment/azure/db_migrations && \
	terraform apply -auto-approve \
    		-var="db_migration_docker_image=$$(cat $(DB_MIGRATION_ARTIFACT_INFO))" \
    		-var="db_type=$(DB_TYPE)" \
    		-var="vault_name=$(DB_VAULT)"

migration_build_and_deploy: ## Build and Deploy Migrations
migration_build_and_deploy: aks_login build_stats_db_migration_image deploy_db_migrations

build: ## build image, which is used for the services
	docker build \
		--target azure_service \
		--build-arg PIP_EXTRA_INDEX_URL=$(PIP_EXTRA_INDEX_URL) \
		-t $(AZURE_REGESTRY_IMAGE_NAME):latest \
		-f $(WORKDIR)/Dockerfile $(WORKDIR);
	docker tag $(AZURE_REGESTRY_IMAGE_NAME):latest $(AZURE_REGESTRY_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	docker push   $(AZURE_REGESTRY_IMAGE_NAME):latest
	docker push   $(AZURE_REGESTRY_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	echo $(AZURE_REGESTRY_IMAGE_NAME):$(AZURE_REGESTRY_TAG)
	echo "$(AZURE_REGESTRY_IMAGE_NAME):$(AZURE_REGESTRY_TAG)" > $(AZ_IMAGE_ARTIFACT_INFO)

deploy_service: ## Deploy stats handler service
	cd $(WORKDIR)/deployment/azure/stats_service && \
	terraform apply -auto-approve \
    		-var="service_image=$$(cat $(AZ_IMAGE_ARTIFACT_INFO))"


build_and_deploy: ## Build and Deploy
build_and_deploy: aks_login build deploy_service
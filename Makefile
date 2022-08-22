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

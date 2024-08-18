# CORE DI STATS HANDLER GEN 1 SRV
Main service purpose is to process and save statistics of entities ingestion or enrichment process


## Content:
1. [Documentation Links](#documentation-links)
2. [Local Development](#local-development)
    - [Prerequisites](#development-prerequisites)
        - [General Prerequisites](#general-development-prerequisites)
        - [Specific Prerequisites: Azure](#azure-development-specific-prerequisites)
    - [Running Service](#running-service)
3. [Testing](#testing)
4. [Deployment](#deployment)
    - [Prerequisites](#deployment-prerequisites)
        - [General Prerequisites](#general-deployment-prerequisites)
        - [Specific Prerequisites: Azure](#azure-specific-deployment-prerequisites)
    - [Running Deploy](#running-deploy)


## Documentation links
- [Architecture Diagram](https://pattern-glove-823.notion.site/Architecture-Documentation-736e81ad2d134e8fa586de738dd14ed8)


## Local Development
List of actions, needed to start develop system on private development environment.

### Development Prerequisites

#### General Development Prerequisites:
1. install docker `version>=20.10.0`
2. install docker-compose `version>=1.29.0`
3. install make util
4. run:
   ```shell
   make git_hooks_init
   ```
5. setup local development environment (check [environments readme](envs/readme.md))
6. run to select default env and follow the instruction. In case, if you do not see list,
   of available environments - please ensure, that you create own env, based on the [envs/example.env](envs/example_env.txt)
   ```shell
   make set_default_env
   ```

### Running service
Main tool for run service locally is docker-compose util.
So run:
1. Before running define env variables like in [example](envs/example_env.txt) file.
2. Run Stats handler and stats db using docker-compose:
   ```shell
   make compose_up
   ```


## Testing:
Before testing make sure, that you have all prerequisites for local development.

To run test locally, use:
```shell
make run_tests
```

## Deployment

### Deployment Prerequisites

#### General Deployment prerequisites:
1. install docker `version>=20.10.0`
2. install make util
3. install terraform `version>=1.0.8`

#### Azure Specific Deployment Prerequisites:
1. install az cli `version>=2.29.0`
2. Login to azure:
   ```shell
   make aks_login
   ```

#### Running Deploy
1. Change dir to deployment related cloud provider(`deployment/{Cloud Prodiver}/`) e.g.:
   ```shell
   cd deployment/azure/
   ```
2. Init terraform:
   ```shell
   terraform init
   ```
3. Change dir to root of repository
   ```shell
   cd ./../..
   ```
4. Build production container:
   ```shell
   make build
   make docker-push
   ```
5. Running deploy:
   ```shell
   make deploy_service
   ```
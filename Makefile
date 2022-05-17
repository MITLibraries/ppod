SHELL=/bin/bash
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)
ECR_REGISTRY_DEV=$(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

help: ## Print this message
	@awk 'BEGIN { FS = ":.*##"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*##/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

### Dependency commands ###
install: ## Install dependencies
	pipenv install --dev

update: install ## Update all Python dependencies
	pipenv clean
	pipenv update --dev
	pipenv requirements

### Test commands ###
test: ## Run tests and print a coverage report
	pipenv run coverage run --source=lambdas -m pytest
	pipenv run coverage report -m

coveralls: test
	pipenv run coverage lcov -o ./coverage/lcov.info

### Lint commands ###
lint: bandit black flake8 isort mypy ## Lint the repo

bandit:
	pipenv run bandit -r lambdas

black:
	pipenv run black --check --diff .

flake8:
	pipenv run flake8 .

isort:
	pipenv run isort . --diff

mypy:
	pipenv run mypy lambdas

### Container commands ###
dist-dev: ## Build docker container
	docker build --platform linux/amd64 \
		-t $(ECR_REGISTRY_DEV)/ppod-dev:latest \
		-t $(ECR_REGISTRY_DEV)/ppod-dev:`git describe --always` \
		-t ppod-dev:latest .

publish-dev: dist-dev ## Build, tag and push
	docker login -u AWS -p $$(aws ecr get-login-password --region us-east-1) $(ECR_REGISTRY_DEV)
	docker push $(ECR_REGISTRY_DEV)/ppod-dev:latest
	docker push $(ECR_REGISTRY_DEV)/ppod-dev:`git describe --always`

update-format-lambda-dev: ## Updates the lambda with whatever is the most recent image in the ecr
	aws lambda update-function-code \
		--function-name ppod-dev \
		--image-uri $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/ppod-dev:latest

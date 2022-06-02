SHELL=/bin/bash
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)
### This is the Terraform-generated header for ppod-dev
ECR_NAME_DEV:=ppod-dev
ECR_URL_DEV:=222053980223.dkr.ecr.us-east-1.amazonaws.com/ppod-dev
FUNCTION_DEV:=ppod-dev
### End of Terraform-generated header ###

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
	pipenv run coverage run --include=ppod.py -m pytest
	pipenv run coverage report -m

coveralls: test
	pipenv run coverage lcov -o ./coverage/lcov.info

### Lint commands ###
lint: bandit black flake8 isort mypy ## Lint the repo

bandit:
	pipenv run bandit -r ppod.py

black:
	pipenv run black --check --diff .

flake8:
	pipenv run flake8 .

isort:
	pipenv run isort . --diff

mypy:
	pipenv run mypy .

### Developer Deploy Commands ###
dist-dev: ## Build docker container (intended for developer-based manual build)
	docker build --platform linux/amd64 \
	    -t $(ECR_URL_DEV):latest \
		-t $(ECR_URL_DEV):`git describe --always` \
		-t $(ECR_NAME_DEV):latest .

publish-dev: dist-dev ## Build, tag and push (intended for developer-based manual publish)
	docker login -u AWS -p $$(aws ecr get-login-password --region us-east-1) $(ECR_URL_DEV)
	docker push $(ECR_URL_DEV):latest
	docker push $(ECR_URL_DEV):`git describe --always`

update-lambda-dev: ## Updates the lambda with whatever is the most recent image in the ecr (intended for developer-based manual update)
	aws lambda update-function-code \
		--function-name $(FUNCTION_DEV) \
		--image-uri $(ECR_URL_DEV):latest

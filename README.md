# ppod

## Development
To install with dev dependencies:
```
make install
```

To run unit tests:
```
make test
```

To lint the repo:
```
make lint
```

## Required ENV
`SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.

`WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.

### To run locally
- Build the container:
  ```bash
  docker build -t ppod .
  ```
- Run the container:
  ```bash
  docker run -p 9000:8080 -e WORKSPACE=dev ppod:latest
  ```
- Post data to the container:
  ```bash
  curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d "{}"
  ```
- Observe output:
  ```
  lambda
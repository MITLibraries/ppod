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
`ACCESS_TOKEN` : The POD access token used to authenticate uploads. The access tokens can be found on the `Manage Organization` page.

`BUCKET` = The bucket containing the compressed MARCXML files to be submitted to POD.

`POD_URL` =  The POD URL which includes the organization code: `https://pod.stanford.edu/organizations/{Organization Code}/uploads?stream=`

`SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.

`STREAM` = The POD stream to use when posting MARCXML records.

`WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.

### To run locally
NOTE: These instructions for running locally don't currently work and functionality has to be verified in our dev AWS account.
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
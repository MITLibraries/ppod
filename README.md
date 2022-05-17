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
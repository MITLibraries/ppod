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
`POD_ACCESS_TOKEN` : The POD access token used to authenticate uploads. The access tokens can be found on the `Manage Organization` page.

`BUCKET` = The bucket containing the compressed MARCXML files to be submitted to POD.

`POD_URL` =  The POD URL which includes the organization code: `https://pod.stanford.edu/organizations/{Organization Code}/uploads?stream=`

`SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.

`WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.


### Verify local changes in Dev1
- Ensure your AWS CLI is configured with credentials for the Dev1 account.
- Publish the lambda function:
  ```bash
  make publish-dev
  make update-lambda-dev
  ```

#### Submit files to POD test stream
Use the `Test` tab on the lambda to `Event JSON` that will match files in the dev1 S3 bucket:

```bash
{
  "filename-prefix": "exlibris/pod/POD_ALMA_EXPORT_20220523"
}
```

Note: If it's been a while since the last POD export from Alma sandbox, there may be no files in the Dev1 S3 export bucket and you may need to run the publishing job from the sandbox.


Observe that the output reflects the correct number of files:

```bash
{
  "files_processed": 2
}
```


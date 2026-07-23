Databricks Job Runner
=============

Application to trigger Databricks jobs from Keboola Connection flows.

**Table of contents:**

[TOC]

Functionality notes
===================

Prerequisites
=============

The component supports two authentication methods against Databricks:

**1. Personal Access Token (PAT)**
 - Generate a Databricks Personal Access Token.

**2. Service Principal (OAuth M2M)**
 - Create a Databricks service principal and generate an OAuth secret for it.
 - Grant the service principal access to the jobs you want to trigger.
 - The component exchanges the client ID and secret for a short-lived workspace
   access token using the OAuth machine-to-machine (client credentials) grant,
   and transparently refreshes it before expiry.

Get the Databricks JOB ID.



Configuration
=============

## Configuration Schema
 - Authentication method (auth_type) - [OPT] `token` (Personal Access Token, default) or `service_principal` (OAuth M2M).
 - Databricks API token (#api_token) - [REQ for `token`] Personal Access Token.
 - Client ID (client_id) - [REQ for `service_principal`] Service principal application (client) ID.
 - Client secret (#client_secret) - [REQ for `service_principal`] Service principal OAuth secret.
 - Base url (base_url) - [REQ] Base URL of the Databricks API instance.
 - Job id (job_id) - [REQ] ID of the DBX job to trigger. Pick it from the list via the "Load jobs" action, or type it manually if the credentials can't list jobs. The "Load jobs" action fails with an explanatory error when no jobs are returned (usually a permissions issue), but you can always enter the ID by hand.
 - Job parameters (job_parameters) - [OPT] Key-value parameters passed to the job run (forwarded as run-now `job_parameters`). Values support Keboola `{{variables}}` and override the job's default parameter values.
 - Wait for job to finish (wait_for_finish) - [OPT] Default `true`. If enabled, the component waits for the triggered job to finish and fails when it does not end with `SUCCESS`. If disabled, it triggers the job and finishes immediately without checking the result.
 - SSL verify (ssl_verify) - [OPT] If false, SSL verification will be turned off and untrusted certificates may be used.


Sample Configuration (Personal Access Token)
=============
```json
{
  "parameters": {
    "auth_type": "token",
    "#api_token": "SECRET_VALUE",
    "base_url": "https://adb-2153812530704740.0.azuredatabricks.net",
    "job_id": "750811009736814",
    "job_parameters": [
      {"key": "environment", "value": "production"},
      {"key": "run_date", "value": "{{run_date}}"}
    ],
    "ssl_verify": true,
    "debug": true
  }
}
```

Sample Configuration (Service Principal / OAuth M2M)
=============
```json
{
  "parameters": {
    "auth_type": "service_principal",
    "client_id": "00000000-0000-0000-0000-000000000000",
    "#client_secret": "SECRET_VALUE",
    "base_url": "https://adb-2153812530704740.0.azuredatabricks.net",
    "job_id": "750811009736814",
    "ssl_verify": true,
    "debug": true
  }
}
```

Output
======

List of tables, foreign keys, schema.

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in
the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/)
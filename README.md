Databricks Job Runner
=============

Application to trigger Databricks jobs from Keboola Connection flows.

**Table of contents:**

[TOC]

Functionality notes
===================

Prerequisites
=============

Get the Databricks API token. 
Get the Databricks JOB ID.



Configuration
=============

## Configuration Schema
 - Databricks API token (#api_token) - [REQ] 
 - Base url (base_url) - [REQ] Base URL of the Databricks API instance.
 - Job id (job_id) - [REQ] ID of the DBX job to trigger.
 - SSL verify (ssl_verify) - [OPT] If false, SSL verification will be turned off and untrusted certificates may be used.


Sample Configuration
=============
```json
{
  "parameters": {
    "#api_token": "SECRET_VALUE",
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
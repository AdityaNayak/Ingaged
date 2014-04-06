Ingaged Frontend
================

## Different Parts

1. `admin` includes the backbone.js based frontend application of the Admin Panel.
2. `customer` includes the backbone.js based frontend application of the Customer Facing Feedback Form.
3. `dashboard` includes the backbone.js based frontend application of the Merchant Dashboard.
4. `assets` includes the all the common assets of admin panel, merchant dashboard and customer facing form.

## Deloying
Experiences (Merchant Dashboard, Customer Facing Feedback Form or Admin Panel) can be deployed to different environment. There
are essentially two types of envrionments: production & staging. In normal scenarios there would be only one production
environment and multiple staging environments.

All the commands related to deployment exist in the `_deployment/deploy.py` file. This file can be run from the console only
when the CWD is the `_deployment` directory.

### Getting a List of Environments
This will list all the available environments. The different headings in the output are essentially the environment names
which can be used in other commands when deploying to those particular environments.

```sh
cd _deployment
python deploy.py list_envs
```

### Creating a New Staging Environments
A unique ID (which should be an incremental ID) for a staging environment needs to given as a parameter to create a new
staging environment.

```sh
cd _deployment
python deploy.py create_staging_env --staging-id {unique integer id}
```

### Deploying to a Particular Environment
The name of the environment and the experience to be deployed are needed when deploying.

1. Name of environment will be among one of the headings of the output of `list_envs` command.
2. Name of the experience can be `customer`, `admin` or `dashboard`.

```sh
cd _deployment
python deploy.py deploy --experience staging-1 --environment customer
```

#### Note on Customer Facing Form Deployment
As `require.js` is being used with the customer facing form, the complete built version of the same is copied to
`to_be_deployed/customer`. The deployment script deploys this version of the customer facing form.

**Note: Currently there are no e-Mails being sent automatically (as opposed to the same during deployment) on the heroku app. So when you deploy a new version, make it a point to intimate everyone else on your own. The best way to do this would be comment on the pull request in github.**

# Ingaged API

API powering the Merchant Dashboard, Customer Facing Feedback Form & Admin Panel. Directory containing this `README.md`
only consists of the flask based APIs. The backbone based frontend is included in the `frontend` directory contained
in the parent of `api` directory.

## Deployment

### Adding Heroku App Git Repos as Remotes
Currently we are using heroku for running python based APIs. There are different apps in heroku. Here is a list of all of them.

#### Production
1. ingage

#### Staging
2. ingage-staging-1

There will be times when a single staging environment will not suffice. In such a case the instructions to create a new
staging environment are explained below in the section titled **Creating a new Staging Environment**

## Creating a new Staging Environment

1. Create a new app on Heroku and name it `ingage-staging-{incremental id}`.

   The `{incremental id}` is +1 incremented to the count of the last staging environment created.

2. Add the MongoHQ addon to the newly created heroku app.

   This can done [MongoHQ AddOn Page](https://addons.heroku.com/mongohq) on heroku. Add this add on with the Sandbox plan.

3. Add the email deploy hooks to this app so that an e-mail is sent whenver a new deployment is made.

   ```shell
   heroku addons:add deployhooks:email \
   --recipient="rishabh@ingagelive.com,aditya@ingagelive.com" \
   --subject="InGage API deployed to a staging environment." \
   --body="{{user}} deployed a new version of {{app}}.\n\nCheck it out on {{url}}.\n\nGit Log of Changes:\n\n{{git_log}}" \
   --app=ingage-staging-{incremental id}
   ```

   The {incremental id} used here would be the same as in step 1.

4. Add this staging environment in the list of staging environments in this `README.md` file.
5. Add the new app's git repo as a remote in your local git repo.

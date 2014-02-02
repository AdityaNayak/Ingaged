Ingaged Frontend
================

## Different Parts

1. `admin` includes the backbone.js based frontend application of the Admin Panel.
2. `customer` includes the backbone.js based frontend application of the Customer Facing Feedback Form.
3. `dashboard` includes the backbone.js based frontend application of the Merchant Dashboard.
4. `assets` includes the all the common assets of admin panel, merchant dashboard and customer facing form.

## Deployment
Here the deployment instructions for deploying **Admin Panel**, **Customer Facing Form** and **Merchant Dashboard**.

1. Run `_deployment/deploy.py` from the shell.

   ```sh
   cd _deployment
   python deploy.py
   ```

2. As assets are in an upper level directory to the dashboard, admin panel or customer facing form. But they will be
   uploaded at the same level under the `assets` directory when being uploaded to S3. So you would have to change the
   references in all the HTML files of the web app.

   **After completeing all the steps don't forget to use `git stash` to to revert the changed references.**

3. Enter the absolute paths of assets directory and the other required directories and choose the other asked options.

4. The files will be uploaded to S3. You will have to enable **Static Web Hosting** using the S3 web panel if required.

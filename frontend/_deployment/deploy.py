# -*- coding: utf-8 -*-
import os, sys

from flask import Flask
from flask.ext.script import Manager
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from clint.textui import progress
from clint.textui import colored

# create a Flask-Script manager for CLI
app = Flask(__name__) # TODO: using flask-script requires a flask app. look into something better for same functionality.
manager = Manager(app)

# AWS Keys
AWS_ACCESS_KEY_ID = 'AKIAI66SF4STC6GMSA6Q'
AWS_SECRET_ACCESS_KEY = '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'

# Creating an S3 connection
conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# current working directory
cwd = os.getcwd()

# buckets & corresponding environments
# this dict has the buckets for production & different staging environments
buckets = {
    'production': {
        'admin': 'admin.ingagelive.com',
        'customer': 'customer.ingagelive.com',
        'dashboard': 'ingagelive.com'
    },
    'staging-1': {
        'admin': 'admin-staging-1.ingagelive.com',
        'customer': 'customer-staging-1.ingagelive.com',
        'dashboard': 'dashboard-staging-1.ingagelive.com'
    },
    'staging-2': {
        'admin': 'admin-staging-2.ingagelive.com',
        'customer': 'customer-staging-2.ingagelive.com',
        'dashboard': 'dashboard-staging-2.ingagelive.com'
    }
}

# bucket names (for staging environment)
staging_bucket_names = {
    'admin': 'admin-staging-{0}.ingagelive.com',
    'customer': 'customer-staging-{0}.ingagelive.com',
    'dashboard': 'dashboard-staging-{0}.ingagelive.com'
}

# absolute paths of directories containing all the resources
get_resource_dir = lambda r_dir: os.path.abspath(os.path.join(cwd, '..', r_dir))
resource_dirs = {
    'assets': get_resource_dir('assets'),
    'admin': get_resource_dir('admin'),
    'customer': get_resource_dir('customer'),
    'dashboard': get_resource_dir('dashboard')
}

# get a list of all filenames in a directory (recursively walks through sub directories too)
def get_dir_filenames(directory):
    """Returns a list of all file names by recursively walking through
    the given directory path using `os.walk`.
    """
    all_filenames = [] # list of all file names
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            all_filenames.append(os.path.join(root, filename))

    return all_filenames

# create a new staging environment
@manager.option('-id', '--staging-id', type=int, dest='id', help="Staging Environment Unique ID.")
def create_staging_env(id):
    """Creates a new staging environment. A staging environment consists
    of 3 buckets. One each for Admin Panel, Customer Facing Feedback Form
    and Merchant Dashboard.

    Note: The names of the buckets are defined in `staging_bucket_names` dict.
    """
    print '\n'
    # names of buckets which will be created
    for k,v in staging_bucket_names.items():
        staging_bucket_names[k] = v.format(id)

    # check if bucket(s) with names of to-be-created buckets exist
    # if any such bucket(s) exist, then throw an error
    all_buckets = [i.name for i in conn.get_all_buckets()]
    if set(all_buckets).intersection(set([v for k,v in staging_bucket_names.items()])):
        print colored.red('This staging environment already seems to exist. Please provide a different ID.')
        return False # TODO: throw an error in this case

    # create buckets
    buckets = {}
    for k,v in staging_bucket_names.items():
        buckets[k] = conn.create_bucket(v)

    # print the new buckets
    print colored.cyan('These buckets were created: ')
    for k,v in buckets.items():
        print colored.blue('{0}: {1}'.format(k,v.name))
    print

    print colored.green('Remember to enable static web hosting for the newly created buckets.')
    print colored.green('Update the github wiki with the newly created staging environment.')
    print colored.green('Also update the `buckets` dictionary to include the newly created staging environment.')
    print colored.green('Everything is done.\n')
    
    return True

# list all environments
@manager.command
def list_envs():
    """Lists all the existing environments. (Both staging & production environments.)
    
    Note: Uses the `buckets` dict to list all environments.
    """
    print '\n'
    for k,v in buckets.items():
        print colored.cyan(k)
        for k,v in buckets[k].items():
            print colored.blue(v)
        print '\n'

# deploys a particular experience to a given environment
@manager.option('-exp', '--experience', dest='exp', required=True,
        help="What needs to be deployed? (dashboard, customer, admin)", choices=['admin', 'customer', 'dashboard'])
@manager.option('-env', '--environment', dest='env', help='Which environment do you want to deploy to?',
        choices=[i for i in buckets.keys()], required=True)
def deploy(exp, env):
    """Deploys the given experience (Merchant Dashboard, Customer Facing Feedback Form or Admin Panel)
    to the given environment.
    
    Note: Experiences can deployed to only the environments listed in `buckets` dict. So it is
          important to list all the newly created environments in the given dict.
    """
    print '\n'
    # all the files which need to be uploaded
    asset_files = [{'filename': i, 'key': os.path.join('assets', i.split('/assets', 1)[1][1:])} \
            for i in get_dir_filenames(resource_dirs['assets'])]
    exp_files = [{'filename': i, 'key': i.split('/'+ exp, 1)[1][1:]} for i in get_dir_filenames(resource_dirs[exp])]
    all_files = exp_files
    all_files.extend(asset_files)
    print colored.blue('{0} number of files need to be uploaded.'.format(len(all_files)))

    # check if the api_root and references to asset locations have been changed
    m = '> Have you changed the references to resources in assets directory and value of `api_root`? '
    local_changes = raw_input(colored.magenta(m))
    if str.lower(local_changes) != 'y':
        print colored.red('Change the asset references and value of `api_root` and restart this process.')
        return False

    # bucket to upload the resources to
    bucket = conn.get_bucket(buckets[env][exp])
    print colored.blue('Resources are being uploaded to the bucket named {0}.'.format(bucket.name))

    # uploading all the resources
    for file_ in progress.bar(all_files, filled_char='='):
        key = Key(bucket)
        key.key = file_['key']
        key.set_contents_from_filename(file_['filename'])
        key.set_acl('public-read')

    print colored.green('All the resources have been uploaded successfully.')
    return False

if __name__ == "__main__":
    if '_deployment' not in cwd:
        sys.exit(colored.red('This script can only be run inside the "_deployment" directory.'))
    manager.run()

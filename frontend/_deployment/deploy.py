import os, sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

# AWS keys for access
AWS_ACCESS_KEY_ID = 'AKIAJPKFYAQXRHIIIPNA'
AWS_SECRET_ACCESS_KEY = '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'

# Creating the S3 connection
conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# getting all filenames recursively from a directory
def get_all_filenames(directory):
    """Returns a list of all file names by recursively walking through
    the given directory path using `os.walk`.
    """
    all_filenames = [] # list of all file names
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            all_filenames.append(os.path.join(root, filename))

    return all_filenames
            

# filenames of all the assets
assets_dir = raw_input("\nEnter the absolute path to the assets directory: ")
assets_filenames = get_all_filenames(assets_dir)
print "Found {0} files in assets directory to upload.\n\n".format(len(assets_filenames))

# filenames of the static web app (dashboard, admin or customer facing form)
print "Make sure that you have changed the asset references in the web app files properly."
app_dir = raw_input("Enter the absolute path to the directory containing static web app: ")
app_filenames = get_all_filenames(app_dir)
print "Found {0} files in web app directory to upload.\n\n".format(len(app_filenames))

# get all buckets & select a bucket to upload to
all_buckets = conn.get_all_buckets()
print "Existing buckets:"
for bucket in all_buckets:
    print bucket.name
upload_to_existing_bucket = raw_input("Would you like to upload the files to an existing bucket? (y/n) ")
if upload_to_existing_bucket is 'y':
    bucket_name = raw_input("Please input the bucket name: ")
    bucket = conn.get_bucket(bucket_name)
elif upload_to_existing_bucket is 'n':
    bucket_name = raw_input("Please input the name of the new bucket: ")
    bucket = conn.create_bucket(bucket_name)
else:
    sys.exit("You did not enter a valid choice.")

# uploading all assets
print "\n\nBeginning to upload {0} assets.".format(len(assets_filenames))
counter = 0
for filename in assets_filenames:
    # upload the file
    key = Key(bucket)
    key.key = os.path.join('assets', filename.split('/assets', 1)[1][1:])
    key.set_contents_from_filename(filename)
    key.set_acl('public-read')

    # showing status
    counter += 1
    if counter % 3 is 0:
        print "{0} out of {1} files have been uploaded.".format(counter, len(assets_filenames))
print "All assets have been uploaded."


# uploading the web app files
print "\n\nBeginning to upload {0} web app files.".format(len(app_filenames))
counter = 0
app_dirname = app_dir.split("/")[-1]
for filename in app_filenames:
    # upload the file
    key = Key(bucket)
    key.key = filename.split(app_dirname, 1)[1][1:]
    key.set_contents_from_filename(filename)
    key.set_acl('public-read')

    # showing status
    counter += 1
    if counter % 3 is 0:
        print "{0} out of {1} files have been uploaded.".format(counter, len(assets_filenames))
print "All web app files have been uploaded."

print "All files have been uploaded. You will have to set up the S3 bucket for static web hosting using the S3 web interface."

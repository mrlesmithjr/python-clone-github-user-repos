#!/usr/bin/env python

from git import Repo
from os.path import expanduser
from pygithub3 import Github
from ConfigParser import SafeConfigParser
import logging
import os

__author__ = "Larry Smith Jr."
__email___ = "mrlesmithjr@gmail.com"
__maintainer__ = "Larry Smith Jr."
__status__ = "Development"
# http://everythingshouldbevirtual.com
# @mrlesmithjr

logging_format = "%(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format)

# Defines users home directory
user_home = expanduser("~")

parser = SafeConfigParser()
parser.read('github.cfg')

# Parse github.cfg file to get user and token
gh_user = parser.get('github', 'user')
gh_user_token = parser.get('github', 'token')

# Define where to clone repos to locally
local_repos_dir = "%s/Git_Projects/Personal/GitHub/%s" % (user_home, gh_user)

# Check for destination to save repositories to
if not os.path.exists(local_repos_dir):
    logging.info("%s is missing, creating..." % local_repos_dir)
    os.makedirs(local_repos_dir)
    logging.info("%s has been created." % local_repos_dir)
else:
    logging.info("%s found, skipping creation." % local_repos_dir)

# Authenticate
gh = Github(user=gh_user, token=gh_user_token)

# List all of users repositories
repos = gh.repos.list().all()

# Iterate through list of users repositories and clone them
for repo in repos:
    repo_dest = "%s/%s" % (local_repos_dir, repo.name)
    logging.info("Cloning %s to %s" % (repo.name, repo_dest))
    Repo.clone_from(repo.ssh_url, repo_dest)



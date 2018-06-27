#!/usr/bin/env python

from os.path import expanduser
from pygithub3 import Github
from ConfigParser import SafeConfigParser
import git
import logging
import os
import sys

__author__ = "Larry Smith Jr."
__email___ = "mrlesmithjr@gmail.com"
__maintainer__ = "Larry Smith Jr."
__status__ = "Development"
# http://everythingshouldbevirtual.com
# @mrlesmithjr

# Defines the log file name and location of where to log to
LOG_FILE = "clone-github-user-repos.log"

console_logging_format = "%(levelname)s: %(message)s"
file_logging_format = "%(levelname)s: %(asctime)s: %(message)s"

# Configuring logger
logging.basicConfig(level=logging.INFO, format=console_logging_format)
logger = logging.getLogger(__name__)

# Capture directory name of log file
LOG_FILE_DIR = os.path.dirname(LOG_FILE)

# Check if log file directory name is in the current folder
if os.path.isdir("./" + LOG_FILE_DIR):
    LOG = "./" + LOG_FILE
# Check if log file directory name is in the parent folder
elif os.path.isdir("../" + LOG_FILE_DIR):
    LOG = "../" + LOG_FILE
# Error out and exit if log file directory name is not found
else:
    logging.error("%s not found, please fix LOG_FILE variable!" % LOG_FILE)
    sys.exit(0)

# Creating file handler for output file
handler = logging.FileHandler(LOG)

# Configuring logging level for log file
handler.setLevel(logging.INFO)

# Configuring logging format for log file
formatter = logging.Formatter(file_logging_format)
handler.setFormatter(formatter)

# Adding handlers to the logger
logger.addHandler(handler)

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
    logger.info("%s is missing, creating..." % local_repos_dir)
    os.makedirs(local_repos_dir)
    logger.info("%s has been created." % local_repos_dir)
else:
    logger.info("%s found, skipping creation." % local_repos_dir)

# Authenticate
gh = Github(user=gh_user, token=gh_user_token)

# List all of users repositories
repos = gh.repos.list().all()

# Setup list to collect repo names for further checking if directories are in your
# local_repos_dir directory that are not in your GitHub repo list
repo_names = []

# Iterate through list of users repositories and clone them
for repo in repos:
    repo_names.append(repo.name)
    repo_dest = "%s/%s" % (local_repos_dir, repo.name)
    if not os.path.exists(repo_dest):
        logger.info("Cloning %s to %s" % (repo.name, repo_dest))
        git.Repo.clone_from(repo.ssh_url, repo_dest)
    else:
        logger.info("%s already exists, skipping clone action..." % repo_dest)
        git_repo = git.Repo(repo_dest)
        logger.info("Checking Git status for repo: %s" % repo.name)
        changed_files = git_repo.index.diff(None)
        if changed_files != []:
            for changed_file in changed_files:
                logger.warning("%s has been modified in %s" % (changed_file.a_path, repo_dest))
        untracked_files = git_repo.untracked_files
        if untracked_files != []:
            logger.warning("The following untracked files %s were found in %s" % (untracked_files, repo_dest))
        origin = git_repo.remotes.origin
        if "github.com" in origin.url:
            try:
                fetch_origin = origin.fetch()[0]
                if fetch_origin.flags == 4:
                    logger.info("GitHub repo: %s origin remote is: %s" % (repo.name, origin.url))
                    logger.info("No pending changes found in GitHub repo: %s" % repo.name)
                else:
                    logger.warning("Pending changes found in GitHub repo: %s" % repo.name)
            except:
                logger.error("Fetching updates for repo: %s failed.." % repo.name)
        else:
            logger.warning("Repo: %s remote origin is not using GitHub." % repo.name)


# Capture all directories in your local_repos_dir
directories = os.listdir(local_repos_dir)

# Setup list to collect repo directories found that are not in your GitHub repo list
missing_repos = []

# Iterate through list of directories captured in your local_repos_dir
for directory in directories:
    if directory not in repo_names:
        dir_path = "%s/%s" % (local_repos_dir, directory)
        if os.path.isdir(dir_path):
            missing_repos.append(directory)

# If missing_repos is not empty iterate through
if missing_repos != []:
    logger.warning("The following directories found in %s are missing from GitHub." % local_repos_dir)
    for missing_repo in missing_repos:
        dir_path = "%s/%s" % (local_repos_dir, missing_repo)
        try:
            git.Repo(dir_path).git_dir
            git_repo = True
        except git.exc.InvalidGitRepositoryError:
            git_repo = False
        if git_repo:
            repo = git.Repo(dir_path)
            remotes = repo.remotes
            logger.warning("Repo: %s Git_Repo: %s Remotes: %s" % (dir_path, git_repo, remotes))
        else:
            logger.warning("Repo: %s Git_Repo: %s" % (dir_path, git_repo))

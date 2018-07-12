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

# Before fetching, remove any remote-tracking references that no longer exist on the remote.
git_fetch_prune = True

# Define where to clone repos to locally
local_repos_dir = "%s/Git_Projects/Personal/GitHub/%s" % (user_home, gh_user)

logger.info("Starting...")

# Check for destination to save repositories to
logger.info("Checking to ensure %s exists." % local_repos_dir)
if not os.path.exists(local_repos_dir):
    logger.info("%s not found, creating..." % local_repos_dir)
    os.makedirs(local_repos_dir)
    logger.info("%s has been successfully created." % local_repos_dir)
else:
    logger.info("%s found, skipping creation." % local_repos_dir)

# Authenticate
logger.info("Authenticating with GitHub API.")
gh = Github(user=gh_user, token=gh_user_token)
logger.info("Successfully authenticated with GitHub API.")

# List all of users repositories
logger.info("Capturing all of users repos from GitHub.")
repos = gh.repos.list().all()
logger.info("All of users repos have been successfully captured.")

# Setup list to collect repo names for further checking if directories are in your
# local_repos_dir directory that are not in your GitHub repo list
repo_names = []

# Iterate through list of users repositories and clone them
for repo in repos:
    logger.info("Processing repo %s ..." % repo.name)
    repo_names.append(repo.name)
    repo_dest = "%s/%s" % (local_repos_dir, repo.name)
    if not os.path.exists(repo_dest):
        logger.info("Repo %s not found locally." % repo.name)
        logger.info("Cloning repo %s locally." % repo.name)
        git.Repo.clone_from(repo.ssh_url, repo_dest, recursive=True)
        logger.info("Repo %s successfully cloned locally." % repo.name)
    else:
        logger.info(
            "Repo %s already exists locally, skipping clone." % repo.name)
        git_repo = git.Repo(repo_dest)
        logger.info("Checking for locally changed files for repo %s" %
                    repo.name)
        changed_files = git_repo.index.diff(None)
        if changed_files != []:
            logger.warning("Changed files for repo %s found..." % repo.name)
            for changed_file in changed_files:
                logger.warning("%s has been modified locally in repo %s" % (
                    changed_file.a_path, repo.name))
        else:
            logger.info(
                "No changed files were found locally for repo %s" % repo.name)
        logger.info(
            "Checking for untracked files locally for repo %s" % repo.name)
        untracked_files = git_repo.untracked_files
        if untracked_files != []:
            logger.warning("Untracked files for repo %s found..." % repo.name)
            for untracked_file in untracked_files:
                logger.warning("%s is untracked locally in repo %s" %
                               (untracked_file, repo.name))
        else:
            logger.info("No untracked files found for repo %s" % repo.name)
        logger.info("Capturing repo %s origin remote." % repo.name)
        origin = git_repo.remotes.origin
        logger.info("Repo %s origin remote captured successfully." % repo.name)
        logger.info("Validating repo %s origin remote is GitHub." % repo.name)
        if "github.com" in origin.url:
            logger.info(
                "Repo %s origin remote validated successfully." % repo.name)
            github_origin = True
        else:
            logger.error(
                "Repo %s origin remote validation failed." % repo.name)
            logger.info("Repo %s origin remote is %s" %
                        (repo.name, origin.url))
            github_origin = False
        if github_origin:
            try:
                logger.info(
                    "Checking for pending changes on GitHub for repo %s" % repo.name)
                fetch_origin = origin.fetch(prune=git_fetch_prune)[0]
                if fetch_origin.flags == 4:
                    logger.info(
                        "No pending changes found on GitHub for repo %s" % repo.name)
                else:
                    logger.warning(
                        "Pending changes found on GitHub for repo %s" % repo.name)
            except:
                logger.error(
                    "Check for pending changes on GitHub for repo %s failed." % repo.name)


# Capture all directories in your local_repos_dir
logger.info("Capturing list of directories in %s" % local_repos_dir)
directories = os.listdir(local_repos_dir)
logger.info("List of directories in %s completed successfully." %
            local_repos_dir)

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
    logger.warning(
        "The following directories found in %s are missing from GitHub." % local_repos_dir)
    for missing_repo in missing_repos:
        dir_path = "%s/%s" % (local_repos_dir, missing_repo)
        logger.warning("Directory %s was not found on GitHub." % dir_path)
        try:
            git.Repo(dir_path).git_dir
            git_repo = True
        except git.exc.InvalidGitRepositoryError:
            git_repo = False
        if git_repo:
            repo = git.Repo(dir_path)
            remotes = repo.remotes
            logger.info("Directory %s is configured as a git repo." % dir_path)
            logger.info("Directory %s is configured with the following git remotes %s" % (
                dir_path, remotes))
        else:
            logger.info(
                "Directory %s is not configured as a git repo." % dir_path)

logger.info("Finished...")

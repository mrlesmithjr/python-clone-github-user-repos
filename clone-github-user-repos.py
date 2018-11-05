#! /usr/bin/env python
"""Just a handy script to clone a GitHub user's repos locally."""

import os
from os.path import expanduser
from ConfigParser import SafeConfigParser
import logging
import sys
from pygithub3 import Github
import git

__author__ = "Larry Smith Jr."
__email___ = "mrlesmithjr@gmail.com"
__maintainer__ = "Larry Smith Jr."
__status__ = "Development"
# http://everythingshouldbevirtual.com
# @mrlesmithjr

# Defines the log file name and location of where to log to
LOG_FILE = "clone-github-user-repos.log"

CONSOLE_LOGGING_FORMAT = "%(levelname)s: %(message)s"
FILE_LOGGING_FORMAT = "%(levelname)s: %(asctime)s: %(message)s"

# Configuring logger
logging.basicConfig(level=logging.INFO, format=CONSOLE_LOGGING_FORMAT)
LOGGER = logging.getLogger(__name__)

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
    logging.error("%s not found, please fix LOG_FILE variable!", LOG_FILE)
    sys.exit(0)

# Creating file handler for output file
HANDLER = logging.FileHandler(LOG)

# Configuring logging level for log file
HANDLER.setLevel(logging.INFO)

# Configuring logging format for log file
FORMATTER = logging.Formatter(FILE_LOGGING_FORMAT)
HANDLER.setFormatter(FORMATTER)

# Adding handlers to the logger
LOGGER.addHandler(HANDLER)

# Defines users home directory
USER_HOME = expanduser("~")

PARSER = SafeConfigParser()
PARSER.read('github.cfg')

# Parse github.cfg file to get user and token
GH_USER = PARSER.get('github', 'user')
GH_USER_TOKEN = PARSER.get('github', 'token')

# Before fetching, remove any remote-tracking references that no longer exist
# on the remote.
GIT_FETCH_PRUNE = True

# Define where to clone repos to locally
LOCAL_REPOS_DIR = "%s/Git_Projects/Personal/GitHub/%s" % (USER_HOME, GH_USER)

LOGGER.info("Starting...")

# Check for destination to save repositories to
LOGGER.info("Checking to ensure %s exists.", LOCAL_REPOS_DIR)
if not os.path.exists(LOCAL_REPOS_DIR):
    LOGGER.info("%s not found, creating...", LOCAL_REPOS_DIR)
    os.makedirs(LOCAL_REPOS_DIR)
    LOGGER.info("%s has been successfully created.", LOCAL_REPOS_DIR)
else:
    LOGGER.info("%s found, skipping creation.", LOCAL_REPOS_DIR)

# Authenticate
LOGGER.info("Authenticating with GitHub API.")
GH = Github(user=GH_USER, token=GH_USER_TOKEN)
LOGGER.info("Successfully authenticated with GitHub API.")

# List all of users repositories
LOGGER.info("Capturing all of users repos from GitHub.")
REPOS = GH.repos.list().all()
LOGGER.info("All of users repos have been successfully captured.")

# Setup list to collect repo names for further checking if directories are in
# your local_repos_dir directory that are not in your GitHub repo list
REPO_NAMES = []

# Iterate through list of users repositories and clone them
for repo in REPOS:
    LOGGER.info("Processing repo %s ...", repo.name)
    REPO_NAMES.append(repo.name)
    repo_dest = "%s/%s" % (LOCAL_REPOS_DIR, repo.name)
    if not os.path.exists(repo_dest):
        LOGGER.info("Repo %s not found locally.", repo.name)
        LOGGER.info("Cloning repo %s locally.", repo.name)
        git.Repo.clone_from(repo.ssh_url, repo_dest, recursive=True)
        LOGGER.info("Repo %s successfully cloned locally.", repo.name)
    else:
        LOGGER.info(
            "Repo %s already exists locally, skipping clone.", repo.name)
        git_repo = git.Repo(repo_dest)
        LOGGER.info("Checking for locally changed files for repo %s",
                    repo.name)
        changed_files = git_repo.index.diff(None)
        if changed_files != []:
            LOGGER.warning("Changed files for repo %s found...", repo.name)
            for changed_file in changed_files:
                LOGGER.warning("%s has been modified locally in repo %s",
                               changed_file.a_path, repo.name)
        else:
            LOGGER.info(
                "No changed files were found locally for repo %s", repo.name)
        LOGGER.info(
            "Checking for untracked files locally for repo %s", repo.name)
        untracked_files = git_repo.untracked_files
        if untracked_files != []:
            LOGGER.warning("Untracked files for repo %s found...", repo.name)
            for untracked_file in untracked_files:
                LOGGER.warning("%s is untracked locally in repo %s",
                               untracked_file, repo.name)
        else:
            LOGGER.info("No untracked files found for repo %s", repo.name)
        LOGGER.info("Capturing repo %s origin remote.", repo.name)
        origin = git_repo.remotes.origin
        LOGGER.info("Repo %s origin remote captured successfully.", repo.name)
        LOGGER.info("Validating repo %s origin remote is GitHub.", repo.name)
        if "github.com" in origin.url:
            LOGGER.info(
                "Repo %s origin remote validated successfully.", repo.name)
            github_origin = True
        else:
            LOGGER.error(
                "Repo %s origin remote validation failed.", repo.name)
            LOGGER.info("Repo %s origin remote is %s", repo.name, origin.url)
            github_origin = False
        if github_origin:
            try:
                LOGGER.info(
                    "Checking for pending changes on GitHub for repo %s",
                    repo.name)
                fetch_origin = origin.fetch(prune=GIT_FETCH_PRUNE)[0]
                if fetch_origin.flags == 4:
                    LOGGER.info(
                        "No pending changes found on GitHub for repo %s",
                        repo.name)
                else:
                    LOGGER.warning(
                        "Pending changes found on GitHub for repo %s",
                        repo.name)
            except:
                LOGGER.error(
                    "Check for pending changes on GitHub for repo %s failed.",
                    repo.name)


# Capture all directories in your local_repos_dir
LOGGER.info("Capturing list of directories in %s", LOCAL_REPOS_DIR)
DIRECTORIES = os.listdir(LOCAL_REPOS_DIR)
LOGGER.info("List of directories in %s completed successfully.",
            LOCAL_REPOS_DIR)

# Setup list to collect repo directories found that are not in your GitHub
# repo list
MISSING_REPOS = []

# Iterate through list of directories captured in your local_repos_dir
for directory in DIRECTORIES:
    if directory not in REPO_NAMES:
        dir_path = "%s/%s" % (LOCAL_REPOS_DIR, directory)
        if os.path.isdir(dir_path):
            MISSING_REPOS.append(directory)

# If missing_repos is not empty iterate through
if MISSING_REPOS != []:
    LOGGER.warning(
        "The following directories found in %s are missing from GitHub.",
        LOCAL_REPOS_DIR)
    for missing_repo in MISSING_REPOS:
        dir_path = "%s/%s", LOCAL_REPOS_DIR, missing_repo
        LOGGER.warning("Directory %s was not found on GitHub.", dir_path)
        try:
            git.Repo(dir_path).git_dir
            git_repo = True
        except git.exc.InvalidGitRepositoryError:
            git_repo = False
        if git_repo:
            repo = git.Repo(dir_path)
            remotes = repo.remotes
            LOGGER.info("Directory %s is configured as a git repo.", dir_path)
            LOGGER.info("Directory %s is configured with the following git" +
                        "remotes %s", dir_path, remotes)
        else:
            LOGGER.info(
                "Directory %s is not configured as a git repo.", dir_path)

LOGGER.info("Finished...")

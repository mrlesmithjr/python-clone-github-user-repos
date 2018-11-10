# python-clone-github-user-repos

The purpose of this repo is for cloning all of your GitHub repositories. Maybe you
have a huge number of repositories and fail to keep track of them all. Well this
can help you out.

## Requirements

### Python2

```bash
virtualenv -p python2 venv
source venv/bin/activate
pip install -r requirements.txt
```

### GitHub User Token

You will need to create a [personal access token](https://github.com/settings/tokens)
within your GitHub account.

### Create User Configuration File

Define a `github.cfg` file which contains the following contents:

```bash
[github]
user = mygithubusername
token = mysupersecrettoken
```

### Required Python Libraries

Install the required Python libraries by executing:

```bash
pip install -r requirements.txt
```

## Execution

```bash
python clone-github-user-repos.py
```

## Logging

Logging has been implemented in order to easily review what was found. The log
by default is `clone-github-user-repos.log` which is also added to [.gitignore](.gitignore).

## License

MIT

## Author Information

Larry Smith Jr.

- [EverythingShouldBeVirtual](http://everythingshouldbevirtual.com)
- [@mrlesmithjr](https://www.twitter.com/mrlesmithjr)
- <mailto:mrlesmithjr@gmail.com>

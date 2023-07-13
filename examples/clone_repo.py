from git import Repo
import git
import os
import uuid
import subprocess


def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def get_random_dir():
    return "/tmp/random-repo" + str(uuid.uuid4())


def retrieve_valid_repo_path(repo_dir: str, git_url: str, retry=5):
    while retry >= 0:
        if os.path.exists(repo_dir):
            if is_git_repo(repo_dir):
                print(f"{repo_dir} is a valid repo dir")
                return repo_dir
            else:
                repo_dir_new = get_random_dir()
                print(f"{repo_dir} is NOT a valid repo dir, trying new dir {repo_dir_new}")
                return retrieve_valid_repo_path(repo_dir_new, git_url, retry-1)

        else:
            repo = Repo.clone_from(git_url, repo_dir)
            assert not repo.bare
            print(f"{repo_dir} NOT exist, clone from {git_url}")
            return repo.git_dir


def main():
    git_url = "https://github.com/kefeimo/volttron-boptest.git"
    # git_url = "https://github.com/ibpsa/project1-boptest.git"
    repo_dir = get_random_dir()
    os.mkdir(repo_dir)

    print(retrieve_valid_repo_path(repo_dir=repo_dir, git_url=git_url))
    # /tmp/random-repo53d92055-d918-4a7a-869b-38ea4ca4b18f is NOT a valid repo dir, trying new dir /tmp/random-repo1378e75e-091a-464f-b4ab-7f384c288b86
    # /tmp/random-repo1378e75e-091a-464f-b4ab-7f384c288b86 NOT exist, clone from https://github.com/kefeimo/volttron-boptest.git
    # /tmp/random-repo1378e75e-091a-464f-b4ab-7f384c288b86/.git


if __name__ == "__main__":
    main()

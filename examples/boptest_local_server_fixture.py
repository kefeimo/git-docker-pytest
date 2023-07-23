import docker
from git import Repo
import git
import os
import uuid
import subprocess
from time import sleep
import docker
from pathlib import Path

client = docker.from_env()


def _is_venv_dir(path, venv_name=".venv"):
    activate_path = os.path.join(path, venv_name, "bin/activate")
    # cmd = f"source {activate_path}"
    print(f"Check path {activate_path}")
    return os.path.exists(activate_path)


def _get_random_dir():
    return "/tmp/random-env-" + str(uuid.uuid4())


def _retrieve_valid_venv_path(venv_dir: str, venv_name: str = ".venv", retry=5):
    while retry >= 0:
        if os.path.exists(venv_dir):
            if _is_venv_dir(venv_dir, ):
                print(f"{venv_dir} is a valid venv dir")
                return venv_dir
            else:
                repo_dir_new = _get_random_dir()
                print(f"{venv_dir} is NOT a valid venv dir, trying new dir {repo_dir_new}")
                return _retrieve_valid_venv_path(repo_dir_new, venv_name, retry-1)

        else:
            cmd = f"python -m venv {venv_name} {venv_dir}/{venv_name}"
            print(f"{venv_dir} NOT exist, Create new .venv at {venv_dir}")
            res = subprocess.check_output(cmd.split(" "))
            print(res)
            return venv_dir


def create_venv(venv_dir: str = None):
    """
    To create a venv at "/tmp/random-env-..."
    if the fed-in `venv_dir` exists, then use the input `venv_dir`,
    otherwise create a venv at "/tmp/random-env-...", e.g., "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
    """
    if not venv_dir:
        venv_dir = _get_random_dir()
    return _retrieve_valid_venv_path(venv_dir=venv_dir)


def get_bin_path(venv_dir: str = None, venv_name=".venv"):
    valid_venv_dir = create_venv(venv_dir)
    return os.path.join(valid_venv_dir, venv_name, "bin")


def check_dependency(venv_dir: str, lib_name: str):
    """
    Check if certain library is installed by pip
    If installed return True, otherwise return None
    e.g., WARNING: Package(s) not found: docker-compos
    """
    cmd = f"{get_bin_path(venv_dir)}/pip show {lib_name}"
    try:
        res = subprocess.check_output(cmd.split(" ")).decode("utf-8")
        for line in res.splitlines():
            print(line)
        return True
    except Exception as e:
        print(e)
        return False


def install_dependency(venv_dir: str, lib_name: str, version: str = "", constrain: str = "=="):
    """
    To construct the pip install command at certain venv bin path,
    e.g.,  /tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/bin/pip install docker-compose
    """
    # Note: check if exists, ignore version not matched
    if check_dependency(venv_dir=venv_dir, lib_name=lib_name):
        print(f"Library `{lib_name}` already installed.")
        return

    if version and constrain:
        sub_cmd = f"{lib_name}{constrain}{version}"
    else:
        sub_cmd = lib_name

    cmd = f"{get_bin_path(venv_dir)}/pip install {sub_cmd}"
    print(f"Executing command `{cmd}`")
    res = subprocess.check_output(cmd, shell=True).decode('utf-8')
    for line in res.splitlines():
        print(line)



def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def _get_random_dir():
    return "/tmp/random-repo" + str(uuid.uuid4())


def retrieve_valid_repo_path(repo_dir: str, git_url: str, retry=5):
    while retry >= 0:
        if os.path.exists(repo_dir):
            if is_git_repo(repo_dir):
                print(f"{repo_dir} is a valid repo dir")
                return repo_dir
            else:
                repo_dir_new = _get_random_dir()
                print(f"{repo_dir} is NOT a valid repo dir, trying new dir {repo_dir_new}")
                return retrieve_valid_repo_path(repo_dir_new, git_url, retry-1)

        else:
            repo = Repo.clone_from(git_url, repo_dir)
            assert not repo.bare
            print(f"{repo_dir} NOT exist, clone from {git_url}")
            return repo.git_dir

def start_boptest_server(repo_dir: str, compose_file_path: str, testcase_name = "testcase1"):
    """
    Start a boptest server/container, then return the container id
    """
    # checkout tags/v0.4.0 or commit 4465066b at master
    repo: git.Repo = Repo(repo_dir)
    commit_id = "4465066b"
    repo.git.checkout(commit_id)

    # start the boptest server
    # compose_file_path = "/home/kefei/project/project1-boptest/docker-compose.yml"
    compose_file_path = os.path.join(repo_dir, "docker-compose.yml")
    cmd = f"docker-compose --file {compose_file_path} up -d"  # Note: remember to use detach mode
    my_env = os.environ.copy()
    my_env["TESTCASE"] = testcase_name
    print(cmd.split(" "))
    res = subprocess.check_output(cmd.split(" "), env=my_env)
    print(f"Executing command `{cmd}`")
    print(res)


    print(f"client.containers.list()")
    print(client.containers.list())
    # assuming only one boptest container is running
    boptest_container = [c for c in client.containers.list() if "boptest" in c.attrs["Name"]][0]
    container = boptest_container
    print(container)
    print(container.attrs)
    print(container.id)

    return container.id



    # container = client.containers.get("project1-boptest_boptest_1")
    # print(container.attrs)
    #
    # print("==sleeping==")
    # sleep(5)
    # cmd = f"docker-compose --file {compose_file_path} down"
    # res = subprocess.check_output(cmd.split(" "), env=my_env)
    # print(res)
    # print(f"client.containers.list()")
    # print(client.containers.list())


if __name__ == "__main__":
    venv_path = "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
    # retrieve_repo_path = create_venv(venv_path)
    # print(retrieve_repo_path)

    # print(get_bin_path(venv_path))

    print(install_dependency(venv_dir=venv_path, lib_name="docker-compose"))  # docker-compose==1.29.2
    print(install_dependency(venv_dir=venv_path, lib_name="GitPython"))  # GitPython==3.1.32

    # res = check_dependency(venv_dir=venv_path, lib_name="GitPython")
    # print(res)
    # res = check_dependency(venv_dir=venv_path, lib_name="docker-compose")
    # print(res)

    ## git clone
    git_url = "https://github.com/ibpsa/project1-boptest.git"
    # repo_dir = get_random_dir()
    # os.mkdir(repo_dir)
    repo_dir = "/tmp/random-repo6f5ee697-de48-4288-88b8-4f62f18a5e4c"

    print(retrieve_valid_repo_path(repo_dir=repo_dir, git_url=git_url))

    ## start boptest
    start_boptest_server(repo_dir=repo_dir, compose_file_path=repo_dir, testcase_name="testcase1")


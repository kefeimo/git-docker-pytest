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


def check_directory_permissions(directory_path):
    if os.access(directory_path, os.R_OK | os.W_OK | os.X_OK):
        print(f"All permissions are granted for the directory: {directory_path}")
        return True
    else:
        print(f"Not all permissions are granted for the directory: {directory_path}")
        return False


def _is_venv_dir(path, venv_name=".venv"):
    activate_path = os.path.join(path, venv_name, "bin/activate")
    # cmd = f"source {activate_path}"
    print(f"Check path {activate_path}")
    return os.path.exists(activate_path)


def _get_random_venv_dir():
    return "/tmp/random-env-" + str(uuid.uuid4())


# def retrieve_valid_venv_path(venv_dir: str = "", venv_name: str = ".venv", retry=5):
#     while retry >= 0:
#         if os.path.exists(venv_dir):
#             if _is_venv_dir(venv_dir, ):
#                 print(f"`{venv_dir}` is a valid venv dir")
#                 return venv_dir
#             else:
#                 venv_dir_new = _get_random_venv_dir()
#                 print(f"`{venv_dir}` is NOT a valid venv dir, trying new dir `{venv_dir_new}`")
#                 cmd = f"python -m venv {venv_name} {venv_dir_new}/{venv_name}"
#                 res = subprocess.check_output(cmd.split(" "))
#                 print(res)
#                 return venv_dir_new
#
#
#
#         else:
#             venv_dir_new = _get_random_venv_dir()
#             print(f"`{venv_dir}` does NOT exist, creating new dir at `{venv_dir_new}`")
#
#             try:
#                 os.mkdir(venv_dir)
#                 return retrieve_valid_venv_path(venv_dir, venv_name, retry - 1)
#             except Exception as e:
#                 print(e)
#                 venv_dir_new = _get_random_venv_dir()
#                 print(f"{venv_dir} does NOT work, trying new dir {venv_dir_new}")
#                 return retrieve_valid_venv_path(venv_dir_new, venv_name, retry - 1)


def _create_venv(venv_dir):
    print("======= creating venv =======")
    venv_name: str = ".venv"
    if os.path.exists(venv_dir) and check_directory_permissions(venv_dir):
        print(f"`{venv_dir}` exists")
    else:
        try:
            os.makedirs(venv_dir)
            print(f"`{venv_dir} does NOT exists, created new dir {venv_dir}")
        except Exception as e:
            print(e)
            venv_dir_new = _get_random_venv_dir()
            os.makedirs(venv_dir_new)
            print(f"`{venv_dir} does NOT exists, created new dir {venv_dir_new}")
            venv_dir = venv_dir_new

    cmd = f"python -m venv {venv_name} {venv_dir}/{venv_name}"
    res = subprocess.check_output(cmd.split(" "))
    print(res)
    print(f"Created venv at {venv_dir}")
    return venv_dir


def retrieve_valid_venv_path(venv_dir: str = None, ):
    """
    - Return the venv_dir if such venv_dir/bin/activate exists
    - Use the `venv_dir` to create a venv if not exists.
    - Create at tmp/random-env-<uuid> if venv_dir left as default
        or cannot create venv at venv_dir
    """
    if venv_dir is None:
        venv_dir_new = _get_random_venv_dir()
        print(f"Creating random venv at {venv_dir_new}")
        venv_dir = _create_venv(venv_dir_new)

    elif _is_venv_dir(venv_dir, ):
        print(f"`{venv_dir}` is a valid venv dir")
    else:
        print(f"`{venv_dir}/.venv` does NOT exist.")
        venv_dir = _create_venv(venv_dir)

    return venv_dir





# def create_venv(venv_dir: str = None):
#     """
#     To create a venv at "/tmp/random-env-..."
#     if the fed-in `venv_dir` exists, then use the input `venv_dir`,
#     otherwise create a venv at "/tmp/random-env-...", e.g., "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
#     """
#     if not venv_dir:
#         venv_dir = _get_random_venv_dir()
#     return retrieve_valid_venv_path(venv_dir=venv_dir)


def _get_bin_path(venv_dir: str = None, venv_name=".venv"):
    valid_venv_dir = retrieve_valid_venv_path(venv_dir)
    return os.path.join(valid_venv_dir, venv_name, "bin")


def check_dependency(venv_dir: str, lib_name: str):
    """
    Check if certain library is installed by pip
    If installed return True, otherwise return None
    e.g., WARNING: Package(s) not found: docker-compos
    """
    cmd = f"{_get_bin_path(venv_dir)}/pip show {lib_name}"
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

    cmd = f"{_get_bin_path(venv_dir)}/pip install {sub_cmd}"
    print(f"Executing command `{cmd}`")
    res = subprocess.check_output(cmd, shell=True).decode('utf-8')
    for line in res.splitlines():
        print(line)


def _is_git_repo(path, repo_name=".repo"):
    repo_path = os.path.join(path, ".repo")
    if not os.path.exists(repo_path):
        return False
    try:
        _ = git.Repo(repo_path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def _get_random_repo_dir():
    return "/tmp/random-repo" + str(uuid.uuid4())


# def retrieve_valid_repo_path(repo_dir: str, git_url: str, retry=5):
#     while retry >= 0:
#         if os.path.exists(repo_dir):
#             if _is_git_repo(repo_dir):
#                 print(f"{repo_dir} is a valid repo dir")
#                 return repo_dir
#             else:
#                 repo_dir_new = _get_random_repo_dir()
#                 print(f"{repo_dir} is NOT a valid repo dir, trying new dir {repo_dir_new}")
#                 repo = Repo.clone_from(git_url, repo_dir_new)
#                 assert not repo.bare
#                 print(f"Cloning from {git_url} to new dir {repo_dir_new}")
#                 # return repo.git_dir  # this has /.git/ at the end
#                 return repo_dir_new
#
#
#         else:
#             # repo_dir_new = _get_random_repo_dir()
#             print(f"{repo_dir} does NOT exist, creating new dir {repo_dir}")
#             # repo = Repo.clone_from(git_url, repo_dir_new)
#             # assert not repo.bare
#             # print(f"Cloning from {git_url} to new dir {repo_dir_new}")
#             # # return repo.git_dir  # this has /.git/ at the end
#             # return repo_dir_new
#             try:
#                 os.mkdir(repo_dir)
#                 return retrieve_valid_repo_path(repo_dir, git_url, retry - 1)
#             except Exception as e:
#                 print(e)
#                 repo_dir_new = _get_random_repo_dir()
#                 print(f"{repo_dir} does NOT work, trying new dir {repo_dir_new}")
#                 return retrieve_valid_repo_path(repo_dir_new, git_url, retry - 1)


def _create_repo(repo_dir, git_url):
    print("======= creating repo =======")
    if os.path.exists(repo_dir) and check_directory_permissions(repo_dir):
        print(f"`{repo_dir}` exists")
    else:
        try:
            git_path = repo_dir + '/.repo'
            os.makedirs(git_path)
            print(f"`{repo_dir} does NOT exists, created new dir {repo_dir}")
        except Exception as e:
            print(e)
            repo_dir_new = _get_random_repo_dir()
            git_path = repo_dir_new + '/.repo'
            os.makedirs(git_path)
            print(f"`{repo_dir} does NOT exists, created new dir {repo_dir_new}")
            repo_dir = repo_dir_new

    git_path = os.path.join(repo_dir, ".repo")
    repo = Repo.clone_from(git_url, git_path)
    assert not repo.bare
    # return repo.git_dir  # this has /.git/ at the end
    print(f"`git clone`d repo at {git_path}")
    return repo_dir


def retrieve_valid_repo_path(repo_dir: str = None, git_url="https://github.com/ibpsa/project1-boptest.git"):
    """
    - Return the repo_dir if such venv_dir/.git exists
    - Use the `repo_dir` to git clone if not exists.
    - Create at tmp/random-repo-<uuid> if repo_dir left as default
        or cannot git clone at repo_dir
    """
    if repo_dir is None:
        repo_dir_new = _get_random_repo_dir()
        print(f"Creating random repo at {repo_dir_new}")
        repo_dir = _create_repo(repo_dir_new, git_url)
    else:
        repo_dir = Path(repo_dir)

    if _is_git_repo(repo_dir, ):
        print(f"`{repo_dir}` is a valid repo")
    else:
        print(f"`{repo_dir}<repo_name>/.git` does NOT exist.")
        repo_dir = _create_repo(repo_dir, git_url)

    return repo_dir



def start_boptest_server(repo_dir: str, venv_bin_path: str, testcase_name="testcase1", ):
    """
    Start a boptest server/container, then return the container id
    """
    # checkout tags/v0.4.0 or commit 4465066b at master
    repo_name = ".repo"
    repo: git.Repo = Repo(os.path.join(repo_dir, repo_name))
    commit_id = "4465066b"
    repo.git.checkout(commit_id)

    # start the boptest server
    # compose_file_path = "/home/kefei/project/project1-boptest/docker-compose.yml"

    compose_file_path = os.path.join(repo_dir, repo_name, "docker-compose.yml")
    cmd = f"{os.path.join(venv_bin_path, 'docker-compose')} --file {compose_file_path} up -d"  # Note: remember to use detach mode
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


def stop_boptest_server(repo_dir: str, venv_bin_path: str):
    """
    Stop a boptest server/container, return docker-compose stdout
    """
    repo_name = ".repo"
    compose_file_path = os.path.join(repo_dir, repo_name, "docker-compose.yml")
    cmd = f"{os.path.join(venv_bin_path, 'docker-compose')} --file {compose_file_path} down"
    res = subprocess.check_output(cmd.split(" "))
    print(f"Executing command `{cmd}`")
    print(res)
    return res


if __name__ == "__main__":

    ## venv
    venv_path = "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
    venv_path = ""
    # venv_path = None
    # venv_path = "/tmp/random-env-babcbc02-da1b-496b-adb3-c9ec856ad68c"
    # retrieve_repo_path = create_venv(venv_path)
    # print(retrieve_repo_path)

    valid_venv_path = retrieve_valid_venv_path(venv_path)
    print(f"valid_venv_path {valid_venv_path}")
    # venv path
    venv_bin_path = _get_bin_path(valid_venv_path)
    #
    print(install_dependency(venv_dir=valid_venv_path, lib_name="docker-compose"))  # docker-compose==1.29.2
    # print(install_dependency(venv_dir=venv_path, lib_name="GitPython"))  # GitPython==3.1.32

    ## git clone
    git_url = "https://github.com/ibpsa/project1-boptest.git"
    # git_url = "https://github.com/kefeimo/git-docker-pytest.git"
    # # # repo_dir = get_random_dir()
    # # # os.mkdir(repo_dir)
    # repo_dir = "/tmp/random-repo6f5ee697-de48-4288-88b8-4f62f18a5e4c"
    repo_dir = ""
    # repo_dir = None
    # # # repo_dir = "/tmp/random-repo3904b7e7-4e49-47da-aa39-da061ea3ff15/"
    # #
    valid_repo_dir = retrieve_valid_repo_path(repo_dir=repo_dir, git_url=git_url)
    print(valid_repo_dir)

    print(_is_git_repo(repo_dir))




    ## start boptest
    container_id = start_boptest_server(repo_dir=valid_repo_dir, venv_bin_path=venv_bin_path, testcase_name="testcase1")
    container = client.containers.get(container_id)
    print(container.attrs)

    sleep(5)

    # stop boptest
    stop_boptest_server(repo_dir=valid_repo_dir, venv_bin_path=venv_bin_path)


import pytest
from git import Repo
import git
import os
import uuid
import subprocess
from time import sleep
import docker
import requests

from boptest_local_server_fixture import start_boptest_server, \
    stop_boptest_server, \
    retrieve_valid_repo_path, _get_bin_path, \
    retrieve_valid_venv_path, install_dependency

client = docker.from_env()

# TODO: use parametrize with fixture instead
# Note: by specifying specific REPO_DIR
REPO_DIR = "/tmp/random-repo6f5ee697-de48-4288-88b8-4f62f18a5e4c"
REPO_DIR = ""
VENV_DIR = "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
VENV_DIR = ""
TEST_CASE = "testcase1"


@pytest.fixture(scope="module")
def boptest_sever():
    ## venv
    venv_path = "/tmp/random-env-3046c3b0-8641-46dc-be44-75141f666ff1/"
    venv_path = ""
    # venv_path = "/tmp/random-env-babcbc02-da1b-496b-adb3-c9ec856ad68c"
    # retrieve_repo_path = create_venv(venv_path)
    # print(retrieve_repo_path)
    venv_path = VENV_DIR
    valid_venv_path = retrieve_valid_venv_path(venv_path)
    print(f"valid_venv_path {valid_venv_path}")
    venv_bin_path = _get_bin_path(valid_venv_path)
    print(install_dependency(venv_dir=valid_venv_path, lib_name="docker-compose"))

    ## git clone
    git_url = "https://github.com/ibpsa/project1-boptest.git"
    repo_dir = REPO_DIR
    print(retrieve_valid_repo_path(repo_dir=repo_dir, git_url=git_url))

    valid_repo_dir = retrieve_valid_repo_path(repo_dir=repo_dir, git_url=git_url)
    print(valid_repo_dir)

    ## start boptest
    testcase_name = TEST_CASE
    container_id = start_boptest_server(repo_dir=repo_dir, venv_bin_path=venv_bin_path,
                                        testcase_name=testcase_name)
    sleep(5)
    yield container_id

    ## stop boptest
    stop_boptest_server(valid_repo_dir, venv_bin_path)


def test_boptest_server_fixture(boptest_sever):
    container_id = boptest_sever
    container = client.containers.get(container_id)
    print("=====================")
    print(container.attrs)

    # verify testcase_name
    cmd = f"curl http://127.0.0.1:5000/name"
    res = subprocess.check_output(cmd.split(" "))
    print("=====================")
    print(res)


# @pytest.mark.skip(reason="for local testing. Assuming a local testcase is running")
class TestDummy:
    """
    Testing BopTestSimIntegrationLocal
    """

    def test_dummy(self):
        print("This is a dummy test")

from git import Repo
import git
import os
import uuid
import subprocess
from time import sleep
import docker
client = docker.from_env()


def is_venv_dir(path, venv_name=".venv"):
    activate_path = os.path.join(path, venv_name, "bin/activate")
    # cmd = f"source {activate_path}"
    print(f"Check path {activate_path}")
    return os.path.exists(activate_path)


def get_random_dir():
    return "/tmp/random-env-" + str(uuid.uuid4())


def retrieve_valid_venv_path(venv_dir: str, venv_name: str = ".venv", retry=5):
    while retry >= 0:
        if os.path.exists(venv_dir):
            if is_venv_dir(venv_dir, ):
                print(f"{venv_dir} is a valid repo dir")
                return venv_dir
            else:
                repo_dir_new = get_random_dir()
                print(f"{venv_dir} is NOT a valid venv dir, trying new dir {repo_dir_new}")
                return retrieve_valid_venv_path(repo_dir_new, venv_name, retry-1)

        else:
            cmd = f"python -m venv {venv_name} {venv_dir}/{venv_name}"
            print(f"{venv_dir} NOT exist, Create new .venv at {venv_dir}")
            subprocess.check_output(cmd.split(" "))
            return venv_dir


def main():
    # path_test = "/home/kefei/project/git-docker-pytest"
    # print(f" path_test, {is_venv_dir(path_test)}")
    # path_test = "/home/kefei/project/volttron-boptest"
    # print(f" path_test, {is_venv_dir(path_test)}")

    random_dir = get_random_dir()
    print(retrieve_valid_venv_path(venv_dir=random_dir))



if __name__ == "__main__":
    main()

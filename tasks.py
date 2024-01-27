"""invoke-terraform helpers v0.8"""

from glob import glob
from os import getcwd, path
from subprocess import PIPE, STDOUT, Popen

from codeowners import CodeOwners
from git import Repo
from invoke import task
from yaml import YAMLError, safe_load


def get_root(c):
    return c.run("git rev-parse --show-toplevel", hide=True).stdout.strip()


def load_cfg(root):
    with open(path.join(root, "config.yaml"), "r") as f:
        try:
            return safe_load(f)
        except YAMLError as exc:
            print(exc)


def filter_run(
    cmd,
    begin="\x1b[1m\x1b[36mNote:\x1b[0m\x1b[1m Objects have changed outside of Terraform",
    end="─────────────────────────────────────────────────────────────────────────────",
):
    "Background run to filter output in realtime"
    skip = False
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
    for line in iter(p.stdout.readline, ""):
        if line.startswith(begin):
            skip = True
        elif line.startswith(end) and skip:
            skip = False
            print(f"'{begin}' has been excluded from output")
        if not skip:
            print(line.rstrip())


@task(
    help={
        "force": "Force refresh .terraform.lock.hcl",
        "clean": "Clean .terraform folder and lock file before",
        "extra": "Extra parameters to pass to terraform",
        "dry": "Dry run only",
    }
)
def init(c, force=False, clean=False, extra="", dry=False):
    """
    terraform init wrapper
    """
    curr = getcwd()
    root = get_root(c)
    cfg_path = path.relpath(curr, root)
    cfg_data = load_cfg(root)
    print(f"terraform init wrapper, path: '{cfg_path}'")

    if not glob(path.join(curr, "*.tf")):
        print("No terraform files found in current path, exit...")
        exit(1)
    if clean:
        c.run("rm -rf .terraform .terraform.lock.hcl")
    # if lock file do not exist in the beginning, force update
    if force or not path.exists(path.join(curr, ".terraform.lock.hcl")):
        print(".terraform.lock.hcl will be updated")
        force = True
    # init S3 backend
    if "s3" in cfg_data["init"]:
        cmd = 'terraform init -backend-config="key={}/terraform.tfstate" {} {}'.format(
            cfg_path,
            " ".join(
                [
                    f'-backend-config="{k}={v}"'
                    for k, v in cfg_data["init"]["s3"].items()
                ]
            ),
            extra,
        )
        if path.exists(path.join(curr, ".static")):
            print("This configuration do not use dynamic backend state, skip...")
        elif not dry:
            if force:
                c.run(cmd, env={"TF_PLUGIN_CACHE_DIR": ""})
            else:
                c.run(cmd)
        else:
            print(f"Dry run, cmdline: '{cmd}'")
    else:
        print("Only S3 backend supported, exit...")
        exit(1)
    # lock file update
    if force and not dry:
        c.run(
            f"terraform providers lock {' '.join([f'-platform={i}' for i in cfg_data['init']['arch']])}",
            env={"TF_PLUGIN_CACHE_DIR": ""},
        )


@task(
    help={
        "extra": "Extra parameters to pass to terraform",
        "dry": "Dry run only",
    }
)
def plan(c, extra="", dry=False):
    """
    terraform plan wrapper
    """
    cmd = ["terraform", "plan"] + (extra.split(" ") if extra else [])
    if dry:
        print(f"Dry run, cmdline: '{' '.join(cmd)}'")
    else:
        filter_run(cmd)


@task(
    help={
        "extra": "Extra parameters to pass to terraform",
        "dry": "Dry run only",
    }
)
def apply(c, extra="", dry=False):
    """
    terraform apply wrapper
    """
    cmd = ["terraform", "apply"] + (extra.split(" ") if extra else [])
    if dry:
        print(f"Dry run, cmdline: '{' '.join(cmd)}'")
    else:
        filter_run(cmd)


@task(
    help={
        "folder": "Path to the folder/file to check",
    }
)
def codeowners(c, folder):
    """
    CODEOWNERS check helper
    """
    with open(path.join(get_root(c), "CODEOWNERS"), "r") as file:
        owner = CodeOwners(file.read())
    print(owner.of(folder))


@task()
def diff(c):
    """
    Show changed things in PR
    """
    change = {"A": "Added", "D": "Deleted", "M": "Modified"}

    r = Repo(get_root(c))
    print("Changed in this branch:")
    for i in r.index.diff("origin/main", R=True):
        print(f"File: {i.a_path}, change: {change.get(i.change_type, i.change_type)}")


@task
def docs(c):
    """
    terraform-docs wrapper
    """
    c.run("terraform-docs markdown . > README.md")

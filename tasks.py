"""invoke-terraform helpers v0.3"""

from glob import glob
from os import getcwd, path

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


@task(
    help={
        "force": "Force refresh .terraform.lock.hcl",
        "clean": "Clean .terraform folder and lock file before",
        "dry": "Dry run only",
    }
)
def init(c, force=False, clean=False, dry=False):
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
        cmd = 'terraform init -input=false -backend-config="key={}" -backend-config="bucket={}" -backend-config="dynamodb_table={}" -backend-config="region={}" -backend-config="profile={}"'.format(
            cfg_path,
            cfg_data["init"]["s3"]["bucket"],
            cfg_data["init"]["s3"]["dynamodb"],
            cfg_data["init"]["s3"]["region"],
            cfg_data["init"]["s3"]["profile"],
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
    if force:
        c.run(
            f"terraform providers lock {' '.join([f'-platform={i}' for i in cfg_data['init']['arch']])}",
            env={"TF_PLUGIN_CACHE_DIR": ""},
        )

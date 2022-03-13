"""invoke-terraform helpers v0.1"""

from os import path

from invoke import task


@task(
    help={
        "force": "Force refresh .terraform.lock.hcl",
        "dry": "Dry run only",
    }
)
def init(c, force=False, dry=False):
    """
    terraform init wrapper
    """
    print("terraform init wrapper")
    # if lock file do not exist in the beginning, force update
    if force or not path.exists(".terraform.lock.hcl"):
        print(".terraform.lock.hcl will be updated")
        force = True
    # terraform init
    if not dry:
        if force:
            c.run("terraform init", env={"TF_PLUGIN_CACHE_DIR": ""})
        else:
            c.run("terraform init")
    else:
        print("Dry run, skip...")
    # lock file update
    if force:
        c.run(
            "terraform providers lock -platform=linux_amd64 -platform=darwin_amd64",
            dry=dry,
            env={"TF_PLUGIN_CACHE_DIR": ""},
        )

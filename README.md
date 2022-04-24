# invoke-terraform

[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

[![Lint Code Base](https://github.com/Nklya/invoke-terraform/actions/workflows/lint.yaml/badge.svg)](https://github.com/Nklya/invoke-terraform/actions/workflows/lint.yaml)

Invoke helper for different terraform related stuff

## How to start

* terraform 0.14+ supported (use tfenv to switch between versions)
* ensure that you have python 3.6+ installed
* install dependencies by `pip install -r requirements.txt`
* S3 bucket only supported so far as state backend

## Tasks

* To get list of all supported tasks, run: `inv --list`

## Docs

To find more on why this project was created and how to use, check these articles:

* [Better make for automation](https://link.medium.com/Ujzts51Bupb)
* [Fix ‘Objects have changed outside of Terraform’ with invoke wrapper](https://link.medium.com/GGsOdW3Bupb)

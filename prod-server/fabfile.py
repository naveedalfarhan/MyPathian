from fabric.api import env, local, lcd, cd, run, put
from fabric.decorators import hosts


def test():
    print("test")
    local("pwd")

def package():
    cwd = local("pwd", True)
    git_root_dir = local("git rev-parse --show-toplevel", True)
    with lcd(git_root_dir):
        zip_file_location = cwd + "/export.zip"
        local("git archive --format zip --output " + zip_file_location + " dev")

@hosts(["pathian-ec2"])
def preclean():
    env.use_ssh_config = True
    with cd("/pathian"):
        run("rm -rf site")


@hosts(["pathian-ec2"])
def deploy():
    env.use_ssh_config = True
    run("mkdir /pathian/site")
    run("chmod g+rwxs /pathian/site")
    with cd("/pathian/site"):
        put("export.zip", "/pathian/export.zip")
        run("unzip ../export.zip")

@hosts(["pathian-ec2"])
def clean():
    env.use_ssh_config = True
    with cd("/pathian"):
        run("rm export.zip")

@hosts(["pathian-ec2"])
def install_packages():
    env.use_ssh_config = True
    with cd("/pathian/env/bin"):
        run("./pip install -r /pathian/site/requirements-pinned.txt")
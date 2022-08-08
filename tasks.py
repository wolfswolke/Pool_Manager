"""

"""
# ------------------------------------------------------- #
#                     imports
# ------------------------------------------------------- #
import os
import shutil
import webbrowser

from invoke import task

# ------------------------------------------------------- #
#                   definitions
# ------------------------------------------------------- #
ARCHIVE_NAME = "PoolManager"
DEVELOP_APP_VERSION = "v99-99-99"
CONFIG_FILE_NAME = "poolmanager"
EXECUTABLE_NAME = "PoolManager"

VIRTUALENV_NAME = "py39_PoolManager"

OPEN_IN_NEW_TAB = 2

# ------------------------------------------------------- #
#                   global variables
# ------------------------------------------------------- #


# ------------------------------------------------------- #
#                      functions
# ------------------------------------------------------- #
def _update_requirements_txt(c):
    c.run("pip freeze > requirements.txt")


def remove_temporary_folders():
    print("-> remove unused folders")
    for folder in ["dist", "build", "temp"]:
        if os.path.exists(folder):
            print("remove: {}".format(folder))
            shutil.rmtree(folder)
    print("finished!")

# ------------------------------------------------------- #
#                      classes
# ------------------------------------------------------- #


# ------------------------------------------------------- #
#                       tasks
# ------------------------------------------------------- #
@task
def create_image_resource(c):
    with c.prefix("workon {}".format(VIRTUALENV_NAME)):
        c.run("pyside2-rcc -o src\\gui\\res\\images.py graphics\\resource.qrc")


@task
def update_requirements(c):
    with c.prefix("workon {}".format(VIRTUALENV_NAME)):
        _update_requirements_txt(c)


@task
def create_exe(c, version="v9-9-9"):
    with c.prefix("workon {}".format(VIRTUALENV_NAME)):

        print("---------- START CREATING EXE ----------")
        remove_temporary_folders()

        print("-> start creating .exe")
        c.run("pyinstaller start_app.spec")
        print("finished!")

        print("-> start creating temporary folders and copy files")
        for folder in ["temp", "temp/logs", "temp/config", "temp/apps", "temp/graphics/",
                       "temp/graphics/rendered", "temp/graphics/rendered/general"]:
            os.mkdir(folder)

        shutil.copyfile("config/DEFAULT_{}.yml".format(CONFIG_FILE_NAME), "temp/config/{}.yml".format(CONFIG_FILE_NAME))
        shutil.copyfile("dist/{}.exe".format(EXECUTABLE_NAME), "temp/apps/{}.exe".format(EXECUTABLE_NAME))

        print("finished!")
        print("-> start creating .zip")

        zip_name = ARCHIVE_NAME + "_" + version

        shutil.make_archive(zip_name, "zip", "temp")
        print("finished!")
        remove_temporary_folders()
        print("---------- FINISHED CREATING EXE ----------")


@task
def encode_string(c, string):
    with c.prefix("workon {}".format(VIRTUALENV_NAME)):
        from gutils.authentication_handle import encode_string_info

        encoded, result = encode_string_info(string)

        if result:
            print("could not encrypt string because -> {}".format(result))
        else:
            print("result -> {}".format(encoded))


@task
def run_unittests(c):
    with c.prefix("workon {}".format(VIRTUALENV_NAME)):
        with c.prefix("cd test"):
            c.run("coverage run -m unittest discover")
            c.run("coverage html")
            webbrowser.open(os.path.abspath("test/htmlcov/index.html"), new=OPEN_IN_NEW_TAB)


@task
def release(cmd, version):
    with cmd.prefix("workon {}".format(VIRTUALENV_NAME)):
        from gputils.git_utils import check_ready_to_release, release_commit
        from gputils.file_utils import set_version_nr_in_file

        if check_ready_to_release():
            set_version_nr_in_file("src/start_app.py", r'APP_VERSION = "v\d+.\d+.\d+"',
                                   'APP_VERSION = "{}"'.format(version))

            create_exe(cmd, version)

            exe_created = False

            if os.path.exists(ARCHIVE_NAME + "_" + version + ".zip"):
                exe_created = release_commit(version)

            set_version_nr_in_file("src/start_app.py", r'APP_VERSION = "v\d+.\d+.\d+"',
                                   'APP_VERSION = "{}"'.format(DEVELOP_APP_VERSION))

            if exe_created:
                cmd.run('git commit -am "minor -set app version to develop"')
                print("going to push changes")
                cmd.run("git push --follow-tags")
                print("git push -> CHECK")

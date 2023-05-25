""" module for ghettorecorder Python package to container deployment (read only, or restore on shutdown fs)

Target
   docker container
   snap container, snapcraft setup for linux OS

Functions
   container_setup  - decide to set up a container env
   container_config_dir - get path for new folder creation
   create_config_env    - overwrite base dir for ghetto, copy config file to that dir
"""
import os
import shutil
import getpass
from ghettorecorder.ghetto_api import ghettoApi


class Helper:
    def __init__(self):
        self.config_dir = ''  # caller can import the path, useful for blacklist path


helper = Helper()


def container_setup():
    """ return False if no package specific env variable is set

     Info
        variable must be set in package config file Dockerfile or snapcraft.yaml
        change and create the default (parent) record path
        copy settings.ini to that path

    :returns: True if container
    """
    is_container = False
    is_snap = 'SNAP' in os.environ
    is_docker = 'DOCKER' in os.environ

    if is_snap:
        get_env_snap()
        is_container = True
        container_config_dir('SNAP')
        return is_container

    if is_docker:
        get_env_docker()
        is_container = True
        container_config_dir('DOCKER')
        return is_container
    return is_container


def get_env_snap():
    print('GhettoRecorder App in Snap Container, check environment:\n')
    print('SNAP_USER_COMMON: ' + os.environ["SNAP_USER_COMMON"])
    print('SNAP_LIBRARY_PATH: ' + os.environ["SNAP_LIBRARY_PATH"])
    print('SNAP_COMMON: ' + os.environ["SNAP_COMMON"])
    print('SNAP_USER_DATA: ' + os.environ["SNAP_USER_DATA"])
    print('SNAP_DATA: ' + os.environ["SNAP_DATA"])
    print('SNAP_REVISION: ' + os.environ["SNAP_REVISION"])
    print('SNAP_NAME: ' + os.environ["SNAP_NAME"])
    print('SNAP_ARCH: ' + os.environ["SNAP_ARCH"])
    print('SNAP_VERSION: ' + os.environ["SNAP_VERSION"])
    print('SNAP: ' + os.environ["SNAP"])


def get_env_docker():
    print('\n\tGhettoRecorder App in Docker Container\n')


def container_config_dir(container):
    """ assemble the path to new config dir (settings.ini and blacklist)
    | 'get user' - create dir under home folder for snap
    | save path for caller to read later

    :params: container: either snap or docker
    """
    if container == 'SNAP':                                   # SNAP
        username = getpass.getuser()
        print('Hello, ' + username)
        ghetto_folder = os.path.join('/home', username, 'GhettoRecorder')
    else:
        ghetto_folder = os.path.join('/tmp', 'GhettoRecorder')  # DOCKER

    create_config_env(ghetto_folder)
    helper.container_path = ghetto_folder


def create_config_env(ghetto_folder):
    """ copy config files outside the default package folder /site-settings/ghettorecorder

    statements
       create new parent record folder
       overwrite radio_base_dir default path where config is searched
       copy settings.ini to that folder, blacklist is created automatically if choice
    """
    make_config_folder(ghetto_folder)
    ghettoApi.config_dir = ghetto_folder
    source_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini')
    dst_ini = os.path.join(ghetto_folder, 'settings.ini')
    container_copy_settings(source_ini, dst_ini)


def make_config_folder(ghetto_folder):
    try:
        os.makedirs(ghetto_folder, exist_ok=True)
        print(f"\tOK: {ghetto_folder}")
    except OSError as error_os:
        print(f"\tDirectory {ghetto_folder} can not be created {error_os}")
        return False


def container_copy_settings(source_ini, dst_ini):
    """ copy settings.ini from package container to
     snap user home/GhettoRecorder or
     docker tmp/GhettoRecorder
     never overwrite a user customized settings.ini
     """
    try:
        if not os.path.exists(dst_ini):
            shutil.copyfile(source_ini, dst_ini)
    except FileExistsError:
        pass

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
from ghettorecorder.api import ghettoApi


def container_setup():
    """ return False if no package specific env variable is set

     Info
        variable must be set in package config file Dockerfile or snapcraft.yaml
        change and create the default (parent) record path
        copy settings.ini to that path
    """
    is_container = False
    is_snap_container = 'GHETTORECORDER_SNAP' in os.environ   # var must be set in package config, some value
    is_docker_container = 'DOCKER' in os.environ              # var must be set in package config, some value

    if is_snap_container:
        print('Snap Container')
        is_container = True
        container_config_dir('SNAP')
        return is_container

    if is_docker_container:
        print('Docker Container')
        is_container = True
        container_config_dir('DOCKER')
        return is_container
    return is_container


def container_config_dir(container):
    """ assemble the path to new config dir (settings.ini and blacklist)

    variable
       get user - create dir under home folder for snap
     """
    if container == 'SNAP':                                   # SNAP
        username = getpass.getuser()
        print('Hello, ' + username)
        ghetto_folder = os.path.join('/home', username, 'GhettoRecorder')
    else:
        ghetto_folder = os.path.join('/tmp', 'GhettoRecorder')  # DOCKER

    create_config_env(ghetto_folder)


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

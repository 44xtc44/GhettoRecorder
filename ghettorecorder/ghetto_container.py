""" Module for ghettorecorder Python package to container deployment.

All container need different folders to store 'settings.ini'.
Some areas are write protected, restored to default after app exit, or the user can not access them.

Methods
    container_setup decide to set up a container env
    container_config_dir get path for new folder creation
    create_config_env overwrite base dir for ghetto, copy config file to that dir
"""
import os
import shutil
import getpass
from ghettorecorder.ghetto_api import ghettoApi


def container_setup() -> str:
    """ return False, empty string if no package specific env variable is set

    Copy settings.ini to the container writable user folder.
    Android Studio copy settings.ini folder from /assets to user folder.
    ./assets/GhettoRecorder /storage/emulated/0/Music/GhettoRecorder.

     *DOCKER* Variable must be set in package config file Dockerfile or snapcraft.yaml

    :returns: string of folder where settings.ini and blacklist.json resides
    """
    folder = ''
    is_snap = 'SNAP' in os.environ
    is_docker = 'DOCKER' in os.environ  # must be set in Docker file
    is_android = 'ANDROID_STORAGE' in os.environ

    if is_snap:
        get_env_snap()  # track snap ver, release beta, edge ...
        username = getpass.getuser()
        print('Hello, ' + username)
        folder = os.path.join('/home', username, 'GhettoRecorder')

    if is_docker:
        print('\n\tGhettoRecorder App in Docker Container\n')
        folder = os.path.join('/tmp', 'GhettoRecorder')

    if is_android:
        print('\n\tGhettoRecorder Android App\n')
        folder = os.path.join('/storage', 'emulated', '0', 'Music', 'GhettoRecorder')

    if folder:
        create_config_env(folder)
    return folder


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
    """ Copy settings.ini and never overwrite a user customized settings.ini. """
    try:
        if not os.path.exists(dst_ini):
            shutil.copyfile(source_ini, dst_ini)
    except FileExistsError:
        pass
    except Exception as e:
        print(e)

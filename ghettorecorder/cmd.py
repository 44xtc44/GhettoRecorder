"""
"""
import os
import sys
import time
import signal
import multiprocessing as mp
from pathlib import Path

import ghettorecorder.ghetto_menu as ghetto_menu
import ghettorecorder.ghetto_procenv as procenv
import ghettorecorder.ghetto_blacklist as ghetto_blacklist
import ghettorecorder.ghetto_container as container
from ghettorecorder.ghetto_api import ghettoApi

mp.set_start_method('spawn', force=True)  # http server process


class Entry:
    def __init__(self):
        self.http_srv = False
        # file system config
        self.dir_name = os.path.dirname(__file__)  # absolute dir path
        self.config_name = "settings.ini"
        self.blacklist_name = "blacklist.json"
        self.radios_parent_dir = ''  # changed if settings GLOBAL 'save_to_dir' changes, blacklist_dir is also that dir
        # radio dicts, lists
        self.runs_meta = True
        self.runs_record = True
        self.runs_listen = True
        self.radio_name_list = []
        self.config_file_radio_url_dict = {}  # all {name: url}
        self.config_file_settings_dict = {}  # blacklist, folders
        self.radio_selection_dict = {}  # selection to rec
        self.shutdown = False
        # HTTP server
        self.no_err_radios = []  # started radios without errors in err dict


entry = Entry()


def init():
    """File system basic info to find the configuration file.
    | Container creates folders in places where writing is allowed.
    """
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    is_container = container.container_setup()
    print('is_container: ', is_container)
    if is_container:
        config_dir = container.helper.config_dir

    ghettoApi.path.config_dir = config_dir
    ghettoApi.path.config_name = entry.config_name


def run_radios(radio_dict):
    """
    Each instance can have its own configuration. Use a Database or json file.

    - instantiate radios in a dict, start instances
    - failed radios are canceled
    - first radio of the ini list starts a http server to listen local buffered sound

    :params: radio_base_dir: parent dir
    :params: radio_dict: radios with url from menu
    """
    for radio, url in radio_dict.items():
        procenv.radio_instance_create(radio, url, **entry.__dict__)

    url_timeout = 15
    start = time.perf_counter()
    while 1:  # minimize wait time
        done = all([True if instance.init_done else False for instance in ghettoApi.radio_inst_dict.values()])
        if done or (round((time.perf_counter() - start)) >= url_timeout):
            break


def radios_error_get():
    """Useful for terminal, where we must start
    all instances at the same time.

    """
    instance_err_dict = {}
    for radio, inst in ghettoApi.radio_inst_dict.items():
        if ghettoApi.radio_inst_dict[radio].error_dict:
            instance_err_dict[radio] = ghettoApi.radio_inst_dict[radio].error_dict
            ghettoApi.radio_inst_dict[radio].cancel()
            print(f' ### cancel radio {radio} ###')

    if len(instance_err_dict):
        print('\n\n --- errors ---\n\n')
        [print(k, v) for k, v in instance_err_dict.items()]
        print('\n\n --- end ---\n\n')

    entry.no_err_radios = [radio for radio in ghettoApi.radio_inst_dict.keys() if radio not in instance_err_dict.keys()]
    return entry.no_err_radios


def show_radios_urls_formatted():
    """Print formatted urls to be able to click listen.
    """
    for radio, url in entry.config_file_radio_url_dict.items():
        print(f'* {radio:<20} {url}')
    print('\n\t---')


def signal_handler(sig, frame):
    """ Terminal: catch Keyboard Interrupt ctrl + c, "signal.signal()" instances listen.

    :params: sig:  SIGTERM
    :params: frame: SIGINT
    """
    ghettoApi.blacklist.stop_blacklist_writer = True
    shutdown()

    print('\nThank you for using the GhettoRecorder module.')
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def shutdown():
    """"""
    radio_lst = procenv.radio_instances_get()
    for radio in radio_lst:
        procenv.del_radio_instance(radio)
    entry.shutdown = True


def main():
    """"""
    init()  # config file to api
    # show main menu and collect radios or update config file
    ghetto_menu.menu_main()

    entry.config_file_radio_url_dict = ghetto_menu.settings_ini_to_dict()
    for radio in entry.config_file_radio_url_dict.keys():
        entry.radio_name_list.append(radio)
    entry.config_file_settings_dict = ghetto_menu.settings_ini_global()
    entry.radio_selection_dict = ghetto_menu.record_read_radios()  # select radio menu input()

    remote_dir = ghettoApi.path.save_to_dir  # terminal menu option, not the default in [GLOBAL] from settings.ini
    if remote_dir:
        entry.radios_parent_dir = Path(ghettoApi.path.save_to_dir)
    else:
        entry.radios_parent_dir = Path(ghettoApi.path.config_dir)

    run_radios(entry.radio_selection_dict)

    show_radios_urls_formatted()
    ghetto_blacklist.init(**entry.__dict__)

    while 1:
        # names_list = [thread.name for thread in threading.enumerate()]
        # print(names_list)
        time.sleep(10)


if __name__ == "__main__":
    main()

"""
"""
import os
import sys
import time
import signal
import multiprocessing as mp
import concurrent.futures
from pathlib import Path

import ghettorecorder.ghetto_menu as ghetto_menu
import ghettorecorder.ghetto_procenv as ghetto_procenv
import ghettorecorder.ghetto_blacklist as ghetto_blacklist
from ghettorecorder.ghetto_api import ghettoApi

mp.set_start_method('spawn', force=True)  # http server process


class Entry:
    def __init__(self):
        # file system config
        self.dir_name = os.path.dirname(__file__)  # absolute dir path
        self.config_name = "settings.ini"
        self.blacklist_name = "blacklist.json"
        self.radios_parent_dir = ''  # changed if settings GLOBAL 'save_to_dir' changes, blacklist_dir is also that dir
        # radio dicts, lists
        self.radio_name_list = []
        self.config_file_radio_url_dict = {}  # all {name: url}
        self.config_file_settings_dict = {}  # blacklist, folders
        self.radio_selection_dict = {}  # selection to rec
        # HTTP server
        self.no_err_radios = []  # started radios without errors in err dict


entry = Entry()


def init():
    """File system basic info to vars.
    """
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    ghettoApi.path.config_dir = config_dir
    ghettoApi.path.config_name = entry.config_name


def run_radios(radios_parent_dir, radio_dict):
    """
    Each instance can have its own configuration. Use a Database or json file.

    - instantiate radios in a dict, start instances
    - failed radios are canceled
    - first radio of the ini list starts a http server to listen local buffered sound

    :params: radio_base_dir: parent dir
    :params: radio_dict: radios with url from menu
    """
    radio_base_conf = {  # substitute 'radio_base_conf' with 'radio' name column in db or use a json file
        'radio_base_dir': os.path.join(radios_parent_dir, "radios"),
        'runs_meta': True,
        'runs_record': True,
        'runs_listen': False,
        'audio_simple_http_queue': ghetto_procenv.procenv.audio_out
    }

    for radio, url in radio_dict.items():
        ghetto_procenv.create_radio_instance(radio, url, **radio_base_conf)

    url_timeout = 15
    start = time.perf_counter()
    while 1:  # minimize wait time
        done = all([True if instance.init_done else False for instance in ghettoApi.radio_inst_dict.values()])
        if done or (round((time.perf_counter() - start)) >= url_timeout):
            break

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


def show_radios_urls_formatted():
    """Print formatted urls to be able to click listen.
    """
    for radio, url in entry.config_file_radio_url_dict.items():
        print(f'* {radio:<20} {url}')
    print('\n\t---')


def http_srv_start():
    """Enable listen capability.
    """
    radio_name = entry.no_err_radios[0]
    radio_url = entry.config_file_radio_url_dict[radio_name]
    ghetto_procenv.streaming_http_srv_start(radio_name, radio_url)


def termination_accelerator(one_radio_instance):
    """Threads closing instances overlapping with a simple function call.

    :params: one_radio_instance: single instance to cancel
    """
    one_radio_instance.cancel()


def signal_handler(sig, frame):
    """ Terminal: catch Keyboard Interrupt ctrl + c, "signal.signal()" instances listen.

    :params: sig:  SIGTERM
    :params: frame: SIGINT
    """
    ghetto_procenv.procenv.proc_end()
    ghetto_procenv.procenv.thread_shutdown = True
    ghetto_procenv.procenv.thread_end()
    [thread.cancel() for thread in ghetto_procenv.procenv.thread_list]  # db thread
    ghettoApi.blacklist.stop_blacklist_writer = True

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = []
        for radio in ghettoApi.radio_inst_dict.keys():
            future = [executor.submit(termination_accelerator, ghettoApi.radio_inst_dict[radio])]
        concurrent.futures.wait(future)
    print('\nThank you for using the GhettoRecorder module.')
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def main():
    """"""
    init()  # config file to api
    # show main menu and collect radios or update config file
    ghetto_menu.menu_main()

    entry.config_file_radio_url_dict = ghetto_menu.settings_ini_to_dict()
    for radio in entry.config_file_radio_url_dict.keys():
        entry.radio_name_list.append(radio)
    entry.config_file_settings_dict = ghetto_menu.settings_ini_global()
    entry.radio_selection_dict = ghetto_menu.record_read_radios()

    remote_dir = ghettoApi.path.save_to_dir  # terminal menu option, not the default in [GLOBAL] from settings.ini
    if remote_dir:
        entry.radios_parent_dir = Path(ghettoApi.path.save_to_dir)
    else:
        entry.radios_parent_dir = Path(ghettoApi.path.config_dir)

    run_radios(entry.radios_parent_dir, entry.radio_selection_dict)
    if not len(entry.no_err_radios):
        print('\n\tAll radios suffer from failures. Exit.\n')
        return

    http_srv_start()
    ghetto_blacklist.init(**entry.__dict__)

    show_radios_urls_formatted()

    while 1:
        time.sleep(1)


if __name__ == "__main__":
    main()

"""Update a json dict file in intervals, like it eisenradio in database does.
All lists are stored in memory. Write to fs list if change occurs. Updates mem list.

:methods: start_ghetto_blacklist_writer_daemon: run the thread for writing blacklists
:methods: run_blacklist_writer: loop to run 'update_radios_blacklists()'
:methods: update_radios_blacklists: read blacklist file and update it if recorder got a new title
:methods: skipped_in_session(radio): recorder refused to write blacklisted titles n-times
 """
import os.path
import time
import copy
import json
import threading
from pathlib import Path

from ghettorecorder.ghetto_api import ghettoApi


class Helper:
    def __init__(self):
        self.radio_name_list = []
        self.config_file_radio_url_dict = {}
        self.blacklist_name = ''
        self.blacklist_dir = ''  # changed if settings GLOBAL 'save_to_dir' changes, blacklist_dir is that dir


helper = Helper()


def init(**kwargs):
    """kwargs is the dump of callers instances dict
    """
    helper.blacklist_name = kwargs['blacklist_name']
    helper.blacklist_dir = kwargs['radios_parent_dir']
    helper.radio_name_list = kwargs['radio_name_list']
    helper.config_file_radio_url_dict = kwargs['config_file_radio_url_dict']

    blacklist_enabled = True if kwargs['config_file_settings_dict']['blacklist_enable'] else False
    ghettoApi.blacklist.blacklist_enable = True if blacklist_enabled else False
    if blacklist_enabled:
        blacklist_enable(kwargs['blacklist_name'])


def blacklist_enable(file_name):
    """Prepare env for blacklist writer

    - get directory of config file to put blacklist in the same directory
    - call to write a new or update an existing blacklist with radios from config file
    - loads the reader json string from written file into the blacklist dictionary
    - writes the blacklist file name to the api, blacklist writer can update file
    - starts the blacklist writer daemon

    :params: blacklist_name: name
     """
    blacklist_dir = helper.blacklist_dir
    blacklist_written = write_blacklist(blacklist_dir, file_name)
    if blacklist_written:
        # return also ok if file exists
        with open(os.path.join(blacklist_dir, file_name), "r", encoding="UTF-8") as str_reader:
            str_json = str_reader.read()
        # write dict to api, each recorder can compare titles of its radio, json converts str to dict
        ghettoApi.blacklist.all_blacklists_dict = json.loads(str_json)
        start_ghetto_blacklist_writer_daemon()


def write_blacklist(bl_path, bl_name):
    """Write new or update blacklist with new radio names.

    :params: bl_path: path to blacklist
    :params: bl_name: name of blacklist json
    """
    path = os.path.join(bl_path, bl_name)
    if not Path(path).is_file():
        return True if populate_new_blacklist(path) else False
    else:
        return True if update_blacklist(path) else False


def populate_new_blacklist(path):
    """ return True if first time populate the blacklist with empty lists
    add new radios to the list, if list already exists

    | this will create a NEW blist
    | dump all radios from settings.ini
    | append a radio from dump list to blist, create first blist entry "was geht?"
    | write blist to fs

    :params: path: to blacklist
    :exception: make write error public
    :rtype: False
    """
    first_key = 'GhettoRecorder (Eisenradio compatible json) message'
    first_msg = 'A json formatted dictionary. Remove titles you want again.'
    radio_bl_dict = {first_key: [first_msg]}

    for name in helper.radio_name_list:
        radio_bl_dict[name] = ['GhettoRecorder - ¿qué pasa?']
    try:
        with open(path, 'w') as writer:
            writer.write(json.dumps(radio_bl_dict, indent=4))  # no indent is one long line
    except OSError as error:
        msg = f"\n\t--->>> error in populate_new_blacklist(), can not create {error} {path}"
        print(msg)
        return False
    return True


def update_blacklist(path):
    """ return True if update existing blacklist json
    read, load in dict, compare with actual settings.ini,
    update loaded dict, write dict

    | Alter an existing blist.
    | Dump all radios from settings.ini
    | Read in existing blacklist from fs
    | Append a radio from dump list to blist, if radio not in blist create first blist entry "was geht?"
    | Rewrite altered blist

    :params: path: to blacklist
    :exception: make write error public
    :rtype: False
    """
    with open(os.path.join(path), "r", encoding="UTF-8") as reader:
        bl_json_dict = reader.read()
    loaded_dict = json.loads(bl_json_dict)

    for radio in helper.radio_name_list:
        if radio not in loaded_dict.keys():
            loaded_dict[radio] = ['GhettoRecorder - ¿qué pasa?']
    try:
        with open(path, 'w', encoding="UTF-8") as writer:
            writer.write(json.dumps(loaded_dict, indent=4))  # no indent is one long line
    except OSError as error:
        msg = f"\n\t--->>> error in terminal_update_blacklist(), can not create {error} {path}"
        print(msg)
        return False
    return True


def start_ghetto_blacklist_writer_daemon():
    """Start a thread, runs forever"""
    threading.Thread(name="ghetto_blacklist_writer", target=run_blacklist_writer, daemon=True).start()
    print(".. blacklist writer daemon started\n")


def run_blacklist_writer():
    """loop, read "recorder_new_title_dict" in api and update json dict file for next session plus
    'ghettoApi.blacklist.all_blacklists_dict[str_radio]'
    """
    while not ghettoApi.blacklist.stop_blacklist_writer:
        update_radios_blacklists()

        for _ in range(15):
            if ghettoApi.blacklist.stop_blacklist_writer:
                break
            time.sleep(1)


def update_radios_blacklists():
    """Compare recorder_new_title_dict['radio5'] with all_blacklists_dict['radio5']"""
    # make a copy of dict to prevent 'RuntimeError: dictionary changed size during iteration'
    recorder_dict_cp = copy.deepcopy(ghettoApi.blacklist.recorder_new_title_dict)

    for radio, new_title in recorder_dict_cp.items():
        if new_title not in ghettoApi.blacklist.all_blacklists_dict[radio]:
            ghettoApi.blacklist.all_blacklists_dict[radio].append(new_title)
            print(f" -> blacklist {radio}: {new_title.encode('utf-8')} [skipped {skipped_in_session(radio)}]")

            blacklist_file = os.path.join(helper.blacklist_dir, helper.blacklist_name)

            try:
                with open(blacklist_file, 'w', encoding="UTF-8") as writer:
                    writer.write(json.dumps(ghettoApi.blacklist.all_blacklists_dict, indent=4))  # no long line
            except OSError as error:
                msg = f"\n\t--->>> error in update_radios_blacklists(), can not create {error} {blacklist_file}"
                print(msg)


def skipped_in_session(radio):
    """Count skipped file writes.

    :params: radio: name of radio
    :returns: number of not written files, due to blacklist
    """
    return len(ghettoApi.blacklist.skipped_in_session_dict[radio])

""" GhettoRecorder config
settings.ini file
"""
import os
import configparser
from pathlib import Path as Pathlib_path
from ghettorecorder.api import ghettoApi


class GIni:
    """ ONLY command line; 'settings.ini' config
    choice of radios can be made via list index number or name of the radio

    Dictionaries
       radio_names_list = []  . list to search radio name via character
       config_stations = {}          . radio, url pairs from [STATIONS] section
       config_global = {}            . extra infos from [GLOBAL] section, SAVE_TO_DIR = f:\2, BLACKLIST_ENABLE = True

    Methods
       show_items_ini_file() . show the content of the ini file to choose from, fill radio_names_list,radio_names_dict
       config_path_test()    . look if we can read the config file
       blacklist_path_set()  . config_path_test success, set blacklist path to settings.ini path
       global_config_show(print_config=False) . extract GLOBAL section from settings.ini
       global_record_path_write(custom_path) . SAVE_TO_DIR = f:/2
       global_blacklist_enable_write(option) . BLACKLIST_ENABLE = True
       config_path_set(config_files_dir)     . on config path change (menu) set blacklist path to settings.ini path
     """

    radio_names_list = []  # search radio name via character
    logo_path = os.path.dirname(os.path.abspath(__file__))  # print ghettorecorder logo to screen
    config_stations = {}  # config section [STATIONS] radio, url pairs
    config_global = {}    # config section [STATIONS] extra infos SAVE_TO_DIR = f:\2, BLACKLIST_ENABLE = True

    @staticmethod
    def show_items_ini_file():
        """ show the content of the ini file to choose from
        fill radio_names_list and radio_names_dict to later validate the choice
         """
        config = GIni.config_path_test()
        try:
            GIni.config_stations = dict(config.items('STATIONS'))
        except AttributeError:
            print("--> GIni.show_items_ini_file(), can not find configuration section [STATIONS] - proceed")
            return

        with open(os.path.join(GIni.logo_path, "ghetto_recorder.ascii"), "r") as reader:
            print(reader.read())

        GIni.radio_names_list = []
        for name in dict(config.items('STATIONS')):
            GIni.radio_names_list.append(name)

        for index, name in enumerate(GIni.radio_names_list):
            print(f'\t{index} \t>> %-20s <<' % name)

        print(' \n Radio stations in your list. --> CHANGED: 42 to 12345')
        print(' Please use "Ctrl + C" to stop the app.\n')
        print('\tCopy/Paste a Radio from >> settings.ini <<, \n\tor type the leading number and press Enter\n')
        print("\t http://localhost:1242/" + " listen to local recorded stream (saves bandwidth)")
        print("\t If blacklist is ON, file: blacklist.json in the same folder as settings.ini")

        return

    @staticmethod
    def config_path_test():
        config = configparser.ConfigParser()  # instantiate imported library to work with .ini files
        try:
            config_file_path = os.path.join(ghettoApi.config_dir, ghettoApi.config_name)
            config.read_file(open(config_file_path))
        except OSError:
            return False
        else:
            # GIni.blacklist_path_set()
            return config

    @staticmethod
    def blacklist_path_set():
        """ set path to blacklist for blacklist writer

        Info:
           store info of config folder path, prevent writing blacklist in SAVE_TO_DIR folder
        """
        ghettoApi.blacklist_dir = ghettoApi.config_dir

    @staticmethod
    def global_config_show():
        """ extract [GLOBAL] section from settings.ini, if available
        GLOBAL can be - not there, empty, or with values (test case)

        Method
           GIni.config_path_test() - exit if no path

        Raise
           show that there is no config, but can proceed without (GIni.config_path_test(), ok)
        """
        config = GIni.config_path_test()
        if config:
            try:
                GIni.config_global = dict(config.items('GLOBAL'))
            except Exception as error:
                print(f'Config found, minor error: {error} - proceed')
                return True

            if not len(GIni.config_global):
                print("--> section [GLOBAL] is empty. No blacklist, or record path set.")
                return True
            else:
                print(f'.. settings.ini [GLOBAL] section: {GIni.config_global}')
                return True

    @staticmethod
    def global_config_push():
        """ return True if [GLOBAL] section exists and has settings
        push setting of [GLOBAL] section from settings.ini in variables,

        Raise
           show that there is no config, but can proceed without (GIni.config_path_test(), ok)
        """
        config = GIni.config_path_test()
        if config:
            try:
                GIni.config_global = dict(config.items('GLOBAL'))
            except Exception as error:
                print(f'Config found, minor error: {error} - proceed')
                return False

            if not len(GIni.config_global):
                print("--> section [GLOBAL] is empty. No blacklist, or record path set.")
                return False
            else:
                for key, val in GIni.config_global.items():
                    if key == "SAVE_TO_DIR".lower():
                        # push path from [GLOBAL]
                        ghettoApi.save_to_dir = val
                    if key == "BLACKLIST_ENABLE".lower():
                        ghettoApi.blacklist_enable = val
                return True

    @staticmethod
    def global_record_path_write(custom_path):
        """ ini config write
        ["GLOBAL"]
        SAVE_TO_DIR = f:/2
        """
        config = configparser.ConfigParser()
        config_file_path = os.path.join(ghettoApi.config_dir, ghettoApi.config_name)
        config.read_file(open(config_file_path))
        config.sections()
        if "GLOBAL" not in config:
            config.add_section('GLOBAL')
        config.set('GLOBAL', 'SAVE_TO_DIR', str(Pathlib_path(custom_path)))  # help to write path for OS
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def global_blacklist_enable_write(option):
        """ ini config write
        ["GLOBAL"]
        BLACKLIST_ENABLE = True
        """
        config = configparser.ConfigParser()
        config_file_path = os.path.join(ghettoApi.config_dir, ghettoApi.config_name)
        config.read_file(open(config_file_path))
        config.sections()
        if "GLOBAL" not in config:
            config.add_section('GLOBAL')
        config.set('GLOBAL', 'BLACKLIST_ENABLE', option)
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def config_path_set(config_files_dir):
        """ Menu 'Set path to config, settings.ini'
        set path to a 'remote' config file (local fs, writable network location)

        Hint
           can have config somewhere and write to save_to_dir path elsewhere, if this option is used
        """
        ghettoApi.config_dir = str(Pathlib_path(config_files_dir))
        ghettoApi.blacklist_dir = str(Pathlib_path(config_files_dir))

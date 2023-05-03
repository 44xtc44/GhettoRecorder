

class GhettoApi:
    """class in a 3rd party module for exposing variables to package modules to avoid circular imports

    instance vars:
       ghetto_measure_dict -- 'radio,elem': txt key, val pairs of header (default None) Grec name: ghetto_measure
       ghetto_audio_stream_dict -- 'radio,audio': queue_data, val pairs to transfer queue buffer to html audio elem
       current_song_dict -- dict with 'radio_name': actual_title key, val pairs for each radio
       ghetto_dict_error -- conn errors on radio start to display on start page & interrupt thread start (default None)
       listen_active_dict -- break transfer to html audio elem if listen stops, also for thread stop (default None)
       recorder_new_title_dict -- radio writes title to dict to compare with db later (default None)
       aac_repair_log -- log for offline aac file repair
       all_blacklists_dict -- each radio: blacklist key, val (default None)
       stop_blacklist_writer -- stop, also from from timer in EisenRadio
       blacklist_enable -- radio looks if it should read its blacklist or not (default None)
       skipped_in_session_dict -- info to show effects of blacklisting per session (default None)
       blacklist_dir - path to ghetto_recorder blacklist json dict
       blacklist_name - short dir name
       blacklist_enable - [GLOBAL] section of config, True or False
       config_dir - absolute path to config file
       config_name - short name of config file
       radio_parent - short name of radio parent dir
       save_to_dir - [GLOBAL] section of config, remote save files
    """

    def __init__(self):
        """default without args"""
        self.ghetto_measure_dict = None
        self.ghetto_audio_stream_dict = None
        self.current_song_dict = None
        self.ghetto_dict_error = None
        self.listen_active_dict = None
        self.recorder_new_title_dict = None
        self.aac_repair_log = None
        self.all_blacklists_dict = None
        self.stop_blacklist_writer = None
        self.blacklist_enable = None
        self.skipped_in_session_dict = None
        self.blacklist_dir = None
        self.blacklist_name = None
        self.blacklist_enable = None
        self.config_dir = None
        self.config_name = None
        self.radio_parent = None
        self.save_to_dir = None

    def init_ghetto_measurements(self, ghetto_measure_dict):
        """" collect metadata from header and measure request time """
        self.ghetto_measure_dict = ghetto_measure_dict

    def init_ghetto_audio_stream(self, ghetto_audio_stream_dict):
        """ transfer buffer queue for an HTML audio element, needs a '/sound/<radio_name>' like endpoint
        dict[key + ',audio': queue.Queue object], can offer multiple stream qualities divided by name
        """
        self.ghetto_audio_stream_dict = ghetto_audio_stream_dict

    def init_current_song_dict(self, current_song_dict):
        """key:radio name, val: title_text from metadata"""
        self.current_song_dict = current_song_dict

    def init_ghetto_dict_error(self, ghetto_dict_error):
        """ key:radio name, val: error, skip radios with error and display the error """
        self.ghetto_dict_error = ghetto_dict_error

    def init_ghetto_listen_active_dict(self, listen_active_dict):
        """ add radio listening {classic: true}, now goa {classic: false} {goa: true} """
        self.listen_active_dict = listen_active_dict

    def init_ghetto_recorder_new_title(self, recorder_new_title_dict):
        """radios write a title from metadata (minus remove_special_chars() in g_recorder, like copied file name)"""
        self.recorder_new_title_dict = recorder_new_title_dict

    def init_ghetto_all_blacklists_dict(self, all_blacklists_dict):
        """a dict where all radios show their blacklist, so recorder can compare title from metadata """
        self.all_blacklists_dict = all_blacklists_dict

    def init_ghetto_stop_blacklist_writer(self, stop_blacklist_writer):
        """timer set stop to kill thread loop"""
        self.stop_blacklist_writer = stop_blacklist_writer

    def init_ghetto_skipped_in_session_dict(self, skipped_in_session_dict):
        """radio writes skipped titles, to show in blacklist html page"""
        self.skipped_in_session_dict = skipped_in_session_dict

    def init_aac_repair_log(self, aac_repair_log):
        """ return True if a thread with action string record or listen is radio-active"""
        self.aac_repair_log = aac_repair_log

    def init_blacklist_dir(self, blacklist_dir):
        """ absolute path to ghetto_recorder blacklist """
        self.blacklist_dir = blacklist_dir

    def init_blacklist_name(self, blacklist_name):
        """ name for ghetto_recorder blacklist, 'blacklist.json' """
        self.blacklist_name = blacklist_name

    def init_blacklist_enable(self, blacklist_enable):
        """ 'True' or 'False' for blacklist usage """
        self.blacklist_enable = blacklist_enable

    def init_config_dir(self, config_dir):
        """ init absolute path to settings.ini """
        self.config_dir = config_dir

    def init_config_name(self, config_name):
        """ name for ghetto_recorder config file, 'settings.ini' """
        self.config_name = config_name

    def init_radio_parent(self, radio_parent):
        """ name for ghetto_recorder radio parent directory, 'radios' """
        self.radio_parent = radio_parent

    def init_save_to_dir(self, save_to_dir):
        """ [GLOBAL] save_to_dir path option """
        self.save_to_dir = save_to_dir


ghettoApi = GhettoApi()

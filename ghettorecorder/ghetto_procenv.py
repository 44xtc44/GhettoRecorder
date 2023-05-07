import threading
import time

import ghettorecorder.ghetto_db_worker as db_worker
import ghettorecorder.ghetto_http_simple as ghetto_http_simple
import multiprocessing as mp

from ghettorecorder import GhettoRecorder
from ghettorecorder.ghetto_api import ghettoApi

mp.set_start_method('spawn', force=True)


class ProcEnv:
    def __init__(self):
        self.thread_list = []
        self.process_list = []
        self.audio_out = mp.Queue(maxsize=1)  # all radios use central q http
        self.thread_shutdown = False

    def proc_end(self):
        for proc in self.process_list:
            proc.kill()
            proc.join()

    def thread_end(self):
        for thread in self.thread_list:
            thread.cancel()
            thread.join()


procenv = ProcEnv()


class FuncThread(threading.Thread):
    """Thread maker.
    """

    def __init__(self, name, func_ref, *args, **kwargs):
        super().__init__()
        # thread
        self.name = name
        self.daemon = True
        self.cancelled = False
        # stuff
        self.func_ref = func_ref  # no ()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """_inst.start()"""
        self.func_ref(*self.args, **self.kwargs)
        self.cancel()

    def cancel(self):
        self.cancelled = True


def create_radio_instance(radio, url, **kwargs):
    """
    """
    radio, url = radio, url
    ghettoApi.radio_inst_dict[radio] = GhettoRecorder(radio, url)
    ghettoApi.radio_inst_dict[radio].radio_base_dir = kwargs['radio_base_dir']
    ghettoApi.radio_inst_dict[radio].runs_meta = kwargs['runs_meta']
    ghettoApi.radio_inst_dict[radio].runs_record = kwargs['runs_record']
    ghettoApi.radio_inst_dict[radio].runs_listen = kwargs['runs_listen']
    ghettoApi.radio_inst_dict[radio].audio_out = procenv.audio_out
    ghettoApi.radio_inst_dict[radio].start()

    SQL = "UPDATE GhettoRecorder SET runs_meta = ?, runs_record = ?, runs_listen = ?  WHERE radio_name = ?"
    data = (kwargs['runs_meta'],
            kwargs['runs_record'],
            kwargs['runs_listen'],
            radio)
    db_worker.table_insert(SQL, data)


def streaming_http_srv_start(radio_name, radio_url):
    """Have a streaming server for the selected radio.
    The *Master* Http server writes db.
    A Thread starts and stops (kill) streaming server processes.
    """
    while 1:
        if radio_name in ghettoApi.radio_inst_dict.keys():  # wait for radio creation
            break

    ghettoApi.radio_inst_dict[radio_name].runs_listen = True  # enable queue

    while not procenv.audio_out.empty():  # cleanup remnants
        procenv.audio_out.get()

    while not ghettoApi.radio_inst_dict[radio_name].content_type:
        time.sleep(.1)
    content_type = ghettoApi.radio_inst_dict[radio_name].content_type
    param_dct = {'radio_name': radio_name, 'radio_url': radio_url,
                 'content_type': content_type,
                 'port': 1242, 'srv_name': 'mr.http.server',
                 'com_queue': procenv.audio_out  # ghettoApi.audio.audio_stream_queue_dict[radio_name]
                 }

    proc = mp.Process(target=ghetto_http_simple.run_http, kwargs=param_dct)
    proc.start()
    procenv.process_list.append(proc)

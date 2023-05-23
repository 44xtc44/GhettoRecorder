import os
import time
import threading
import multiprocessing as mp

import ghettorecorder.ghetto_net as net
from ghettorecorder.__init__ import GhettoRecorder  # without __init__ broken
from ghettorecorder.ghetto_api import ghettoApi

dir_name = os.path.dirname(__file__)
mp.set_start_method('spawn', force=True)


class ProcEnv:
    def __init__(self):
        self.msg_bin = None
        self.thread_list = []
        self.process_dct = {}
        self.port_dct = {}
        self.thread_shutdown = False  # from cmd
        self.instance_start_dict = {}

    def proc_end(self):
        """"""
        for proc_name in self.process_dct.keys():
            self.process_dct[proc_name].kill()

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


def radio_instances_get():
    """"""
    r_lst = [radio for radio in ghettoApi.radio_inst_dict.keys()]
    return r_lst


def del_radio_instance(radio):
    """
    | Cancel radio instance.
    | Kill http server for streaming to port ... if any
    | Delete all dictionary entries. We can start fresh again.
    """

    inst_dct = ghettoApi.radio_inst_dict
    if radio not in inst_dct.keys():
        return
    try:
        ghettoApi.radio_inst_dict[radio].cancel()
        ghettoApi.radio_inst_dict[radio].join()
        q_lst = [inst_dct[radio].com_in, inst_dct[radio].com_out, inst_dct[radio].audio_out]
        for q in q_lst:
            while not q.empty():
                q.get()
            q.cancel_join_thread()
        del ghettoApi.radio_inst_dict[radio]
        if radio in procenv.process_dct.keys():
            procenv.process_dct[radio].kill()
        if radio in procenv.process_dct.keys():
            del procenv.process_dct[radio]
        if radio in procenv.port_dct.keys():
            del procenv.port_dct[radio]
    except Exception as e:
        print(f'Exception: del_radio_instance ', radio, e)
    print(f'[removed] {radio} from dictionary ')


def radio_instance_create(radio, url, **kwargs):
    """Start radio if not exist.
    """
    if radio in ghettoApi.radio_inst_dict.keys():  # runs already
        return True
    resp = net.load_url(url)
    if not resp:
        print(f'NO connection for instance: {radio} ')
        return False

    radio, url = radio, url
    meta, record, listen, base_dir = True, True, True, dir_name
    if len(kwargs):
        base_dir = kwargs['radios_parent_dir']
        meta, record, listen = kwargs['runs_meta'], kwargs['runs_record'], kwargs['runs_listen']

    ghettoApi.radio_inst_dict[radio] = GhettoRecorder(radio, url)
    ghettoApi.radio_inst_dict[radio].radio_base_dir = base_dir
    ghettoApi.radio_inst_dict[radio].runs_meta = meta
    ghettoApi.radio_inst_dict[radio].runs_record = record
    ghettoApi.radio_inst_dict[radio].runs_listen = listen
    ghettoApi.radio_inst_dict[radio].com_in = mp.Queue(maxsize=1)
    ghettoApi.radio_inst_dict[radio].com_out = mp.Queue(maxsize=1)
    ghettoApi.radio_inst_dict[radio].audio_out = mp.Queue(maxsize=1)
    ghettoApi.radio_inst_dict[radio].start()
    return True


def radio_wait_online(radio):
    """"""
    start = time.perf_counter()
    timeout = 15
    while 1:  # minimize wait time
        in_ = ghettoApi.radio_inst_dict[radio].com_in
        out_ = ghettoApi.radio_inst_dict[radio].com_out
        msg = (radio, 'eval', 'getattr(self, "init_done")')  # tuple
        in_.put(msg)
        done = out_.get()[2]  # tuple
        if done or round((time.perf_counter() - start)) >= timeout:
            break
        time.sleep(.2)


def radio_attribute_get(radio=None, attribute=None):
    """Eval request of instance.

    :params: radio: name
    :params: attribute: string of attribute name
    """
    if radio not in ghettoApi.radio_inst_dict.keys():
        return None
    radio_wait_online(radio)

    in_ = ghettoApi.radio_inst_dict[radio].com_in
    out_ = ghettoApi.radio_inst_dict[radio].com_out
    msg = (radio, 'eval', 'getattr(self, "' + attribute + '")')  # tuple
    in_.put(msg)
    return out_.get()[2]  # tuple


def radio_attribute_set(radio=None, attribute=None, value=None):
    """"""
    if radio not in ghettoApi.radio_inst_dict.keys():
        return None
    radio_wait_online(radio)
    in_ = ghettoApi.radio_inst_dict[radio].com_in
    out_ = ghettoApi.radio_inst_dict[radio].com_out
    in_.put((radio, 'exec', 'setattr(self, "' + attribute + '", ' + value + ')'))
    procenv.msg_bin = out_.get()[2]  # useless msg, just see it was done


def user_display_dict_get(radio):
    """"""
    user_display_dct = {'title': None,
                        'bit_rate': None,
                        'radio_dir': None,
                        'content': None,
                        'radio_name': radio,
                        'recorder': None}

    if radio not in ghettoApi.radio_inst_dict.keys():
        return user_display_dct

    content_type, bit_rate, new_title, radio_dir = "content_type", "bit_rate", "new_title", "radio_dir"
    user_display_dct = {'title': radio_attribute_get(radio=radio, attribute=new_title),
                        'bit_rate': radio_attribute_get(radio=radio, attribute=bit_rate),
                        'radio_dir': radio_attribute_get(radio=radio, attribute=radio_dir),
                        'content': radio_attribute_get(radio=radio, attribute=content_type),
                        'radio_name': radio,
                        'recorder': None}
    return user_display_dct

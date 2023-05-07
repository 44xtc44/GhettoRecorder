import os
import time
import unittest
import threading
import multiprocessing as mp
from collections import namedtuple

import ghettorecorder.ghetto_utils as utils
from ghettorecorder import GhettoRecorder
from ghettorecorder.ghetto_api import ghettoApi
dir_name = os.path.dirname(__file__)  # absolute dir path


class TestDBWorker(unittest.TestCase):
    """
    """
    def setUp(self) -> None:

        ComQ = namedtuple('ComQ', "com_in com_out")
        self.com_q = ComQ(mp.Queue(maxsize=1), mp.Queue(maxsize=1))
        self.radio, url = 'nachtflug', 'http://85.195.88.149:11810'
        radios_parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))

        kwargs = {
            'radio_base_dir': os.path.join(radios_parent_dir, "radios"),
            'runs_meta': True,
            'runs_record': False,
            'runs_listen': True,
        }
        ghettoApi.radio_inst_dict[self.radio] = GhettoRecorder(self.radio, url, com_q=self.com_q)
        ghettoApi.radio_inst_dict[self.radio].radio_base_dir = kwargs['radio_base_dir']
        ghettoApi.radio_inst_dict[self.radio].runs_meta = kwargs['runs_meta']
        ghettoApi.radio_inst_dict[self.radio].runs_record = kwargs['runs_record']
        ghettoApi.radio_inst_dict[self.radio].runs_listen = kwargs['runs_listen']
        ghettoApi.radio_inst_dict[self.radio].start()
        while 1:
            if self.radio in ghettoApi.radio_inst_dict.keys():  # wait for self.radio creation
                break

        while not ghettoApi.radio_inst_dict[self.radio].init_done:
            time.sleep(.1)

    def test_instance_control(self):
        """Run instance default setup.
        Switch listen to false. Shutdown.

        All eval(), except
        exec: to run command; if eval_str[:5] == 'exec:'
        """
        self.com_q.com_in.put('2 * 2')  # test works at all
        result = self.com_q.com_out.get()
        assert 4 == result
        self.com_q.com_in.put('self.runs_listen')
        result = self.com_q.com_out.get()
        assert result
        self.com_q.com_in.put('exec: setattr(self, "runs_listen", False)\n')  # no rv, no out queue
        self.com_q.com_in.put('self.runs_listen')
        result = self.com_q.com_out.get()
        assert not result
        self.com_q.com_in.put('exec: self.cancel()')

        timeout = 10
        start = time.perf_counter()
        while utils.thread_is_up(self.radio + '_meta'):  # minimize wait time, meta thread is up
            time.sleep(.1)
            if round((time.perf_counter() - start)) >= timeout:
                assert 1 == 42
        names_list = [thread.name for thread in threading.enumerate()]
        print(names_list)

    def tearDown(self) -> None:

        while not self.com_q.com_in.empty():
            self.com_q.com_in.get()

        while not self.com_q.com_out.empty():
            self.com_q.com_out.get()

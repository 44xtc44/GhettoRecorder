import os
import time
import unittest
import multiprocessing as mp
from ghettorecorder import GhettoRecorder
dir_name = os.path.dirname(__file__)  # absolute dir path


class TestDBWorker(unittest.TestCase):
    """COM_IN interface to queue test.
    """

    def setUp(self) -> None:
        """Prepare qs and attributes for ghetto recorder instance creation in a process.
        """
        self.dct = {}
        self.PROCS_MAX = 2
        self.proc_list = []
        self.com_in_q_lst = [mp.Queue(maxsize=1), mp.Queue(maxsize=1)]  # process 1, 2
        self.com_out_q_lst = [mp.Queue(maxsize=1), mp.Queue(maxsize=1)]
        self.audio_out_q_lst = [mp.Queue(maxsize=1), mp.Queue(maxsize=1)]
        self.radio_name_1 = 'nachtflug'
        self.radio_name_2 = 'hirschmilch'  # spare part
        self.radio_lst = [
            ('nachtflug', 'http://85.195.88.149:11810'),
            ('hirschmilch', 'https://hirschmilch.de:7001/prog-house.mp3')
        ]
        radios_parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.radio_base_dir = os.path.join(radios_parent_dir, "radios")
        self.kwargs = {}

        self.kwargs.update({'START_SEQUENCE_NUM': 0})
        self.kwargs.update({'radio_base_dir': self.radio_base_dir})
        self.kwargs.update({'radio': self.radio_lst[0]})
        self.kwargs.update({'com_in': self.com_in_q_lst[0]})
        self.kwargs.update({'com_out': self.com_out_q_lst[0]})
        self.kwargs.update({'audio_out': self.audio_out_q_lst[0]})

        proc = mp.Process(target=self.in_proc_radio_create,
                          kwargs=self.kwargs)
        proc.start()
        self.proc_list.append(proc)

    def test_input_queue(self):
        """Check command output returns. Listen Off.
        """

        for i in range(3):
            time.sleep(1)

        cmd_tup = (self.radio_name_1, 'exec', 'setattr(self,"runs_listen", False)')
        self.com_in_q_lst[0].put(cmd_tup)

        out = self.com_out_q_lst[0].get()
        assert out == (self.radio_name_1, 'exec', None)  # None means command executed successful

    def test_audio_queue(self):
        """Check arrival of HTTP request data in audio_out q. Listen On.
        """
        cmd_tup = (self.radio_name_1, 'exec', 'setattr(self,"runs_listen", True)')
        self.com_in_q_lst[0].put(cmd_tup)
        time.sleep(3)
        out = self.audio_out_q_lst[0].get()
        assert isinstance(out, bytes)

    @staticmethod
    def in_proc_radio_create(**kwargs):
        """Create a Ghetto Recorder instance inside a process.
        """
        print(f"in_proc_radio_create {kwargs['radio']}")
        radio, url = kwargs['radio']

        dct = {radio: GhettoRecorder(radio, url)}
        dct[radio].radio_base_dir = (kwargs['radio_base_dir'])
        dct[radio].runs_meta = False  # metadata from radio (name title news)
        dct[radio].runs_record = True  # recorder thread runs
        dct[radio].runs_listen = False  # audio out
        # dct[radio].info_dump_dct = {}
        dct[radio].com_in = kwargs['com_in']
        dct[radio].com_out = kwargs['com_out']
        dct[radio].audio_out = kwargs['audio_out']
        dct[radio].start()

        timeout = 5
        start = time.perf_counter()
        while 1:  # await header info dump
            end = time.perf_counter()
            if dct[radio].info_dump_dct or (end - start) > timeout:
                break
            time.sleep(.1)

    def tearDown(self) -> None:
        for proc in self.proc_list:
            proc.kill()


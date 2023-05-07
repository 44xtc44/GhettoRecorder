"""GhettoRecorder,

Grab hundreds of radio stations ``simultaneously``.
Until your ISP limit hits. OMG it's broken!

"""
import io
import os
import ssl
import time
import random
import certifi
import threading
import multiprocessing as mp  # http srv in a process
from collections import defaultdict  # list as value, return 0 if empty

import ghettorecorder.ghetto_net as ghetto_net
import ghettorecorder.ghetto_meta as ghetto_meta
import ghettorecorder.ghetto_utils as ghetto_utils
import ghettorecorder.ghetto_recorder as ghetto_recorder
import ghettorecorder.ghetto_db_worker as ghetto_db_worker
from ghettorecorder.ghetto_api import ghettoApi  # hope to get rid of it
from ghettorecorder.ghetto_agents import agent_list

dir_name = os.path.dirname(__file__)  # absolute dir path
os.environ['SSL_CERT_FILE'] = certifi.where()
context_ssl = ssl.create_default_context(cafile=certifi.where())


class GhettoRecorder(threading.Thread):
    """
   * Switch features ON/OFF, during runtime
   * Use different configurations for each radio. Use a dict, json file or database (like ``EisenRadio`` FrontEnd).
   * own stream reader modules for mp3 and aac file header included, to repair recorded files on the fly

    __init__(name, url, com_q=None)

    :params: name: custom alias for the inet radio server
    :params: url: url, or playlist deployment server; see 'resolve_playlist_url()'
    :params: com_q: requires a named tuple with in out qs, com_q.com_in.put() or com_q.com_out.put()
    """

    def __init__(self, name, url, com_q=None):
        super(GhettoRecorder, self).__init__()

        # inherited class attributes
        self.name = name
        self.daemon = True
        self.cancelled = False

        # radio instance attributes
        self.time_stamp = None  # can sort db for active radios since
        self.com_q = com_q  # named tuple with in out qs, com_q.com_in.put() or com_q.com_out.put()
        self.bit_rate = None
        self.content_type = None
        self.suffix = ""  # inet radio, or local file system file (fake) stream file extension. See ghetto_streamer.
        self.buf_size = None  # write OS specific multiple of block size
        self.radio_name = name
        self.radio_url = url
        self.chunk = b''
        self.error_dict = defaultdict(list)  # {name: [list of errors,]}
        self.radio_base_dir = "/home/radios"
        self.radio_dir = "/home/radios/fm1/"  # radio_base_dir + instance radio name
        self.rec_src = "/home/radios/fm1/__ghettorecorder.f16"  # recorder file source
        self.rec_dst = ""  # /home/radios/fm1/foo.f16  # recorder file copy destination
        self.new_dst = "/home/radios/fm1/bar.f16"  # path build from the newest metadata, will get destination
        self.bin_writer = None  # recorder file binary writer
        self.new_title = ""  # current metadata title
        self.old_title = ""  # archived previous title
        self.user_agent = ""  # random user agent
        self.user_agent_get()
        self.init_done = False  # caller can loop over instances and proceed if all done
        self.recorder_thread = self.radio_name + '_' + 'rec'  # recorder worker
        self.metadata_thread = self.radio_name + '_' + 'meta'  # metadata worker
        self.worker_aid_thread = self.radio_name + '_' + 'aid'  # restarts worker threads
        self.remote_control_thread = self.radio_name + '_' + 'remote_control'  # exec db orders, stop threads ...
        self.test_loop_thread = self.radio_name + '_' + 'test_loop'
        self.worker_threads = [  # shutdown control list; append your feature threads
            self.recorder_thread,
            self.metadata_thread,
            self.worker_aid_thread,
            self.remote_control_thread,
            self.test_loop_thread
        ]

        self.shutdown = False
        self.record_stop = False  # kills the recording thread loop
        self.meta_data_inst = ghetto_meta.MetaData()
        self.audio_out = None  # connect a queue here to grab response chunks; web server can loop through to a browser
        self.audio_stream_queue = mp.Queue(maxsize=1)  # mem leak plug, buffer size calc in radio_init() bit_rate_get

        # inbuilt features, switched from other modules
        self.runs_meta = False  # call metadata periodically, create path for rec out; False: recorder is the file
        self.runs_record = False  # disable writing to recorder file at all (record blacklist)
        self.recorder_file_write = True  # allow dumping a recorder file (blacklist)
        self.runs_listen = False  # disable write to audio output queue; 3rd party can grab it. (listen blacklist)

    def run(self):
        """Spawn Thread --> _instance.start().
        run() 'works' in the current (main) thread. It doesn't spawn a new thread.
        """
        self.radio_init()

    def cancel(self):
        """Cancel Thread --> _instance.cancel()"""
        self.shutdown = True
        self.shutdown_recorder()
        ghetto_utils.thread_shutdown_wait(*self.worker_threads)
        self.cancelled = True  # kill this thread, our instance sits on

    def shutdown_recorder(self):
        """Close connections and files.

        :methods: teardown: dumps last file and marks it incomplete
        """
        if self.runs_meta and self.runs_record:  # else recorder file is the last file
            self.runs_record = False  # chunks discarded
            ghetto_recorder.teardown(str_radio=self.radio_name,
                                     bin_writer=self.bin_writer,
                                     rec_src=self.rec_src,
                                     rec_dst=self.rec_dst)
        self.runs_meta = False
        self.runs_listen = False
        self.runs_record = False

    def user_agent_get(self):
        """We are a Browser.
        """
        self.user_agent = agent_list[random.randint(0, len(agent_list) - 1)]

    def radio_init(self):
        """Init API and instance attributes.
        Leave the radio instance running, on error. To investigate the cause.
        """
        self.init_ghetto_api()
        if self.resolve_playlist_url() and self.evaluate_response_header():
            self.build_folders()
            self.open_recorder_file()
            self.init_done = True
            print(f'  {self.radio_name} init done')

            self.start_worker_threads()

    def resolve_playlist_url(self):
        """Some Radios use a deployment system.
        A central server offers valid URLs in a playlist file.
        The 'real' radio server URL. We use the first URL.
        """
        pls_m3u_resolved = ghetto_net.pls_m3u_resolve_url(self.radio_url)
        if pls_m3u_resolved:
            self.radio_url = pls_m3u_resolved
        else:
            self.error_writer(self.radio_name, 'Init Connection Failed')
        return True if pls_m3u_resolved else False

    def evaluate_response_header(self):
        """Scan data stream for mp3 and aac bit rates.
        Fall back to header information on error. Several stations send invalid header.
        Get size of buffer to calculate chunk size for writing to fs and listen queue.

        :exception: file extension of stream not available, keep instance running for error evaluation
        :returns: True; 'None' on error, Main can read error_dict and cancel the thread.
        """
        response = ghetto_net.load_url(self.radio_url, self.user_agent)
        if not response:
            self.error_writer(self.radio_name, f' --->  {self.radio_name} no response.')
            return

        try:
            self.suffix = ghetto_net.stream_filetype_url(response, self.radio_name)
        except Exception as unknown_err:
            self.error_writer(self.radio_name, f' --->  {self.radio_name} {unknown_err}')
            return

        self.content_type = ghetto_net.content_type_get(response)
        br_head = response.headers["icy-br"] if "icy-br" in response.headers.keys() else None
        br_data = ghetto_net.bit_rate_get(response.read(io.DEFAULT_BUFFER_SIZE), self.suffix)
        self.bit_rate = br_data if br_data else (int(br_head) if br_head else None)
        if not self.bit_rate:
            self.error_writer(self.radio_name, 'No bit rate found.')
            return

        self.buf_size = ghetto_net.calc_buffer_size(self.bit_rate)
        return True

    def init_ghetto_api(self):
        """Init API attributes to feed external modules and frontend.
        3rd party can use existing dicts to add more dicts
        """
        ghettoApi.audio.audio_stream_queue_dict[self.radio_name] = self.audio_stream_queue  # Html audio element
        ghettoApi.audio.audio_stream_suffix_dict[self.radio_name] = self.suffix  # file extension
        ghettoApi.audio.audio_stream_content_type_dict[self.radio_name] = self.content_type
        ghettoApi.blacklist.all_blacklists_dict[self.radio_name] = {}
        ghettoApi.blacklist.skipped_in_session_dict[self.radio_name] = []  # skipped writes per session
        ghettoApi.err.error_dict[self.radio_name] = ''
        ghettoApi.err.radio_err_count_dict[self.radio_name] = 0
        ghettoApi.feature.feature_mgr_dict[self.radio_name] = {}  # each {'feat. func name has an': own manager inst.}

    def build_folders(self):
        """Create Path names from attributes and write folders to fs.
        """
        self.radio_dir = os.path.join(self.radio_base_dir, self.radio_name)
        many_radios_write_fs_delay = random.random()
        time.sleep(many_radios_write_fs_delay + 0.05)
        msg = f"\tDirectory {self.radio_dir} can not be created\nExit"
        if not ghetto_utils.make_dirs(self.radio_name, self.radio_dir):
            self.error_writer(self.radio_name, msg)

    def open_recorder_file(self):
        """Make a copy of recorder file, reset seek and flush on title change.
        """
        self.rec_src = os.path.join(self.radio_dir, '__ghetto_recorder' + self.suffix)
        self.bin_writer = open(self.rec_src, 'wb')

    def start_worker_threads(self):
        """Meta extracts new titles from metadata requests.
        It creates file names from title, if title is available.
        Meta creates the path for the recorder file dump.
        """
        if self.runs_meta:
            self.radio_metadata_run()
            for seconds in range(5):
                if self.rec_dst:
                    break
                time.sleep(1)
        if self.runs_record or self.runs_listen:
            self.radio_recorder_run()

        self.radio_worker_aid_run()
        self.radio_db_remote_control_run()
        if self.com_q:
            threading.Thread(name=self.test_loop_thread, target=self.radio_test_loop, args=()).start()

    def radio_test_loop(self):
        while 1:

            eval_str = self.com_q.com_in.get()
            if eval_str[:5] == 'exec:':  # exec() returns nothing
                exec(eval_str[6:])
                continue
            print(eval_str)
            result = None
            try:
                result = eval(eval_str)
            except Exception as e:
                print(e)
            self.com_q.com_out.put(result)

    def radio_db_remote_control_run(self):
        """Thread switches feat. via Database interface; Frontend or DB browser
        """
        threading.Thread(name=self.remote_control_thread, target=self.radio_db_remote_control,
                         args=(), ).start()

    def radio_db_remote_control(self):
        """Multiprocessor communication via database.
        Dynamically created database table to read properties.
        Static table to switch settings.

        * 'instance_start_stop' looks for stop order
        * 'feature_start_stop' runs_meta, runs_listen, ...

        """
        # attributes dump, without a leading underscore; no refactor circular import
        dump_dct = GhettoRecorder(self.radio_name, self.radio_url).__dict__  # dead instance, need getattr for values
        attr_dct = {str(key): str(val) for key, val in dump_dct.items() if not key[:1] == '_'}  # str for db

        ghetto_db_worker.db_clean_up_start_env(self)
        col_count = ghetto_db_worker.db_count_table_cols()
        ghetto_db_worker.db_alter_table_cols(col_count, attr_dct)
        ghetto_db_worker.db_create_rows(self)

        while 1:
            if self.shutdown:
                break
            ghetto_db_worker.db_remote_control_loop(self, attr_dct)
            time.sleep(1)

    def radio_worker_aid_run(self):
        """"""
        threading.Thread(name=self.worker_aid_thread, target=self.radio_worker_aid, args=(), ).start()

    def radio_worker_aid(self):
        """Switch worker threads on, if setting is on.
        Helps to switch settings via database.
        """
        while not self.shutdown:
            time.sleep(1)
            if self.runs_meta and not ghetto_utils.thread_is_up(self.metadata_thread):
                self.radio_metadata_run()
            if (self.runs_record and not self.record_stop) and not ghetto_utils.thread_is_up(self.recorder_thread):
                self.radio_recorder_run()

    def radio_metadata_run(self):
        """Start Metadata thread. Runs forever.
        Meta shall construct first and all following title paths.
        """
        print(f'  {self.radio_name} metadata start')
        threading.Thread(name=self.metadata_thread, target=self.radio_metadata_get, args=(), ).start()

    def radio_recorder_run(self):
        """Start Recorder thread. Runs forever.
        """
        threading.Thread(name=self.recorder_thread, target=self.radio_grab, args=(), ).start()
        dual = ' record and listen mode'
        record = ' record mode'
        listen = ' listen mode'
        mode = dual if self.runs_record and self.runs_listen else (record if self.runs_record else listen)
        print(f'  {self.radio_name} recorder ON', mode)

    def error_writer(self, radio, err_msg):
        """Write errors to dict with multiple values. Dict value is a list.
        ghettoApi msg for frontend, Html user output.

        :params: radio: radio name
        :params: err_msg: error message
        """
        self.error_dict[radio].append(err_msg)
        api_err_msg = ghettoApi.err.error_dict[radio]
        ghettoApi.err.error_dict[radio] = api_err_msg + ' :: ' + err_msg
        print(err_msg)

    def radio_metadata_get(self):
        """Radio title extraction from metadata for display and fs copy.

        :methods: metadata_title_change: prints to screen; manage rec dump to file
        :exception: temp URL error, no data or network garbage; absorb up to error count or judgement day
        """
        while 1:
            if self.runs_meta:
                self.meta_data_inst.meta_get(self.radio_url, self.radio_name,
                                             self.radio_dir,
                                             self.suffix, self.bit_rate, self.user_agent)
                self.new_title = self.meta_data_inst.title
                self.new_dst = self.meta_data_inst.title_path

                if self.new_title:
                    self.metadata_title_change()
                    ghettoApi.info.current_title_dict[self.radio_name] = self.new_title

            for sec in range(4):  # 4 x .5 sec
                time.sleep(.5)
                if not self.runs_meta or self.shutdown:
                    ghetto_utils.shutdown_msg(self.radio_name, 'Meta Thread')
                    return

    def metadata_title_change(self):
        """Print title and update ``new_title`` to terminal screen.
        """
        if self.rec_dst != self.new_dst:
            if self.rec_dst and self.runs_record:
                self.rec_dump(self.rec_dst)

            self.rec_dst = self.new_dst
            self.old_title = self.new_title
            print(f' ... Title: [{self.radio_name}]: {self.new_title.encode()} {self.bit_rate} kB\\s')

    def radio_grab(self):
        """Get connection.
        Feed listen queue and recorder file on file system.
        """
        response = ghetto_net.load_url(self.radio_url, self.user_agent)
        while 1:
            self.chunk = self.read_bytes(response)
            if self.chunk:
                self.write_chunk_fs(self.chunk)

                if self.runs_listen:
                    # print('self.runs_listen ', self.chunk)
                    if self.audio_out and not self.audio_out.full():
                        self.audio_out.put(self.chunk)
                    if not self.audio_stream_queue.full():
                        self.audio_stream_queue.put(self.chunk)

            if self.record_stop or self.shutdown:
                ghetto_utils.shutdown_msg(self.radio_name, 'Recorder Thread')
                return

    def read_bytes(self, response):
        """Read a piece of the response bytes.

        :exception: error handler checks severity of the error; run or exit
        :params: response: bytes of internet radio stream
        """
        try:
            chunk = response.read(self.buf_size)
            return chunk
        except Exception as e:
            self.error_handling(e, 'read_bytes')

    def rec_dump(self, rec_dst):
        """Copy recorder file with meta title name to user file.
        We use this chunk as end, and beginning for the next user file.
        Write last chunk (repair if aac), dump recorder file, reset, write first chunk (repair if aac).

        :methods: copy_dst: includes 'blacklist' logic, dump recorder file to destination or not
        :exception: error handler checks severity of the error; run or exit
        :params: rec_dst: absolute path to user file
        """
        ghetto_recorder.record_write_last(self.chunk, self.bin_writer, self.suffix)
        if self.recorder_file_write:
            ghetto_recorder.copy_dst(self.radio_name, rec_dst, self.bin_writer, self.rec_src, self.buf_size)
        self.recorder_file_write = True  # disallow one title

        ghetto_recorder.bin_writer_reset_file_offset(self.bin_writer)
        try:
            ghetto_recorder.record_write_first(self.chunk, self.bin_writer, self.suffix)
        except Exception as e:
            self.error_handling(e, 'rec_dump')

    def write_chunk_fs(self, chunk):
        """Write to recorder file. First and last chunk of .aac will be repaired on 'rec_dump'.

        :exception: error handler checks severity of the error; run or exit instance
        :params: chunk: response stream chunk
        """
        try:
            if self.runs_record:
                self.bin_writer.write(chunk)
        except Exception as e:
            self.error_handling(e, 'write_chunk_fs')

    def error_handling(self, e, meth_name):
        """Handle errors for read and write bytes of
        stream reader/writer functions.
        A cancel() will kill the radio thread.

        :params: e: error object
        """
        weak_error_list = ['BrokenPipeError', 'OSError', 'ValueError']
        strong_error_list = ['ConnectionResetError', 'TypeError']

        if type(e).__name__ in weak_error_list:
            pass
        elif type(e).__name__ in strong_error_list:
            msg = f"Error, {self.radio_name} {meth_name} {type(e).__name__} - cancel radio connection."
            print(msg)
            self.cancel()
        else:
            msg = f"Unknown error, {self.radio_name} {meth_name} {type(e).__name__} - cancel radio connection."
            print(msg)
            self.cancel()


def main(radio='nachtflug', url='http://85.195.88.149:11810', test=None):
    """Not executed if imported as module, but can be called explicitly.
    """

    from collections import namedtuple
    ComQ = namedtuple('ComQ', "com_in com_out")
    com_q = ComQ(mp.Queue(maxsize=1), mp.Queue(maxsize=1))

    mp.set_start_method('spawn', force=True)  # http server in process, fork is deprecated in py 3.14

    radio_base_dir = os.path.join(dir_name, "radios")
    audio_out_q = mp.Queue(maxsize=1)  # start web server in a process

    ghettoApi.radio_inst_dict[radio] = GhettoRecorder(radio, url, com_q=com_q)
    ghettoApi.radio_inst_dict[radio].radio_base_dir = radio_base_dir
    ghettoApi.radio_inst_dict[radio].runs_meta = True
    ghettoApi.radio_inst_dict[radio].runs_record = True
    ghettoApi.radio_inst_dict[radio].runs_listen = True
    ghettoApi.radio_inst_dict[radio].audio_out = audio_out_q
    ghettoApi.radio_inst_dict[radio].start()  # needs while loop to keep main() alive here

    while 1:  # minimize wait time
        func_ref, args = ghetto_db_worker.query_tbl_ghetto_recorder, ['init_done', radio]
        done = True if func_ref(*args) == 'True' else False
        if done:
            break

    param_http = {'radio_name': radio, 'radio_url': url,
                  'content_type': ghetto_db_worker.query_tbl_ghetto_recorder('content_type', radio),
                  'port': 1242, 'srv_name': 'mr.http.server',
                  'com_queue': audio_out_q  # shared queue, can be used to switch inet radio output with local audio
                  # 'com_queue': ghettoApi.audio.audio_stream_queue_dict[radio]  # api default queue
                  }
    import ghetto_http_simple

    proc = mp.Process(target=ghetto_http_simple.run_http, kwargs=param_http)
    proc.start()

    if test:
        time.sleep(5)

        SQL = "UPDATE GRAction SET runs_listen = ? WHERE radio_name = ?;"
        data = (False, radio)
        ghetto_db_worker.table_insert(SQL, data)
        print('update table GRAction runs_listen = False')
        SQL = "UPDATE GRAction SET runs_record = ? WHERE radio_name = ?;"
        data = (False, radio)
        ghetto_db_worker.table_insert(SQL, data)
        print('update table GRAction runs_record = False')
        time.sleep(15)

        SQL = "UPDATE GRAction SET stop = ? WHERE radio_name = ?;"
        data = (True, radio)
        ghetto_db_worker.table_insert(SQL, data)  # shutdown radio via database
        print('update table GRAction stop')

    while 1:
        time.sleep(42)


if __name__ == '__main__':
    main(test=True)

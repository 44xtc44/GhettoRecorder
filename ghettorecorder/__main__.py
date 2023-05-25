"""*Multithreading* server frontend,
  else we stuck on one radio playing and we (the module) can not accept new requests.

| Threads started before socket connect.
| Means, connect gets a random http handler thread, already active.
| Have a timeout to disconnect from radio audio_out connector (queue), handler release.
"""
import os
import time
import json
import socket
import pathlib
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

import ghettorecorder.cmd as cmd
import ghettorecorder.ghetto_menu as menu
import ghettorecorder.ghetto_utils as utils
import ghettorecorder.ghetto_procenv as procenv
from ghettorecorder.cmd import entry  # instance [GLOBAL] [STATIONS] ini sections
from ghettorecorder.ghetto_api import ghettoApi
dir_name = os.path.dirname(__file__)


class Helper:
    def __init__(self):
        self.content_type = None
        self.server_shutdown = False


helper = Helper()


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Ajax SENDs id or name strings.
        self.path is independent of post and get
        """
        if self.path == '/radio_btn_id':
            self.post_switch_radio()
        elif self.path == '/title_get':
            self.post_title_get()
        elif self.path == '/write_config_file':
            self.post_write_config_file()
        elif self.path == '/get_config_file':
            self.post_get_config_file()
        elif self.path == '/write_blacklist_file':
            self.post_write_blacklist_file()
        elif self.path == '/get_blacklist_file':
            self.post_get_blacklist_file()
        elif self.path == '/server_shutdown':
            self.post_server_shutdown()
        elif self.path == '/wait_shutdown':
            self.post_wait_shutdown()
        else:
            self.send_error(404, '[POST] wrong endpoint /<endpoint_name>')

    def do_GET(self):

        if self.path == '/':
            self.get_index_html()
        elif '/sound/' in self.path:
            radio = self.path[7:]  # skip 7 chars, read string to end
            self.get_sound(radio)
        elif '/shutdown/' in self.path:
            radio = self.path[10:]
            self.get_shutdown(radio)
        elif '/static/js/' in self.path:
            js = self.path[11:]
            self.get_js(js)
        elif self.path == '/static/css/style.css':
            self.get_style_css()
        elif '/static/images/' in self.path:
            img = self.path[15:]
            self.get_image(img)
        else:
            self.send_error(404, '[GET] wrong endpoint /<endpoint_name>')

    def post_wait_shutdown(self):
        """JS has timeout"""
        self.data_string_get()
        dct = wait_shutdown()
        self.data_json_send(dct)

    def post_server_shutdown(self):
        """"""
        self.data_string_get()
        dct = server_shutdown()
        self.data_json_send(dct)

    def post_get_blacklist_file(self):
        """"""
        self.data_string_get()
        dct = read_blacklist_file()
        self.data_json_send(dct)

    def post_write_blacklist_file(self):
        """"""
        file_content = self.data_string_get()
        dct = write_blacklist_file(file_content.decode('utf-8'))
        self.data_json_send(dct)

    def post_get_config_file(self):
        """"""
        self.data_string_get()
        dct = read_config_file()
        self.data_json_send(dct)

    def post_write_config_file(self):
        """"""
        file_content = self.data_string_get()
        dct = write_config_file(file_content.decode('utf-8'))
        self.data_json_send(dct)

    def post_title_get(self):
        """data_string_get contains name of radio we want to check for new title. {'title': new_title}"""
        active_radio_name = self.data_string_get()
        dct = radio_title_get(active_radio_name.decode('utf-8'))
        self.data_json_send(dct)

    def post_switch_radio(self):
        """data_string_get contains name of radio we want to switch online.
        Contains Zero int '0' if first call. We disable cover to enable audio, browser demands this step.
        """
        radio_name = self.data_string_get()
        dct = switch_local_buffer(radio_name.decode('utf-8'))
        self.data_json_send(dct)

    def data_json_send(self, data):
        """Send a dictionary here.
        | First key can be identifier for ajax to validate correct delivery. {'foo_transfer': null, 'bar': 'fake_news'}
        | if (!data.foo_transfer) {return;}
        """
        json_string = json.dumps(data)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.flush_headers()
        self.wfile.write(bytes(json_string, "utf-8"))

    def data_string_get(self):
        length = int(self.headers.get_all('content-length')[0])
        data_string = self.rfile.read(length)
        self.send_response(200)
        return data_string

    def get_js(self, js):
        self.send_response(200)
        self.send_header('Content-type', 'text/javascript')
        self.end_headers()
        with open(os.path.join(dir_name, 'static', 'js', js), 'r', encoding='utf-8') as f:
            txt = f.read()
        self.wfile.write(bytes(txt, "utf-8"))

    def get_style_css(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        with open(os.path.join(dir_name, 'static', 'css', 'style.css'), 'r', encoding='utf-8') as f:
            txt = f.read()
        self.wfile.write(bytes(txt, "utf-8"))

    def get_image(self, img):
        self.send_response(200)
        self.send_header('Content-type', 'image/svg+xml')
        self.end_headers()
        with open(os.path.join(dir_name, 'static', 'images', img), 'r', encoding='utf-8') as f:
            txt = f.read()
        self.wfile.write(bytes(txt, "utf-8"))

    def get_shutdown(self, radio):
        """"""
        self.send_response(200)
        self.end_headers()
        procenv.del_radio_instance(radio)

    def get_sound(self, radio=None):
        """The browser audio element (net client) auto connects /sound and is served here, no json return
        We stuck here in a loop and THIS Handler Thread is not able to respond to other requests.
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # absolute essential for using gain and analyzer
        self.send_header('Cache-Control', 'no-cache, no-store')  # absolute essential to not replay old saved stuff
        self.send_header('Content-type', helper.content_type)
        self.end_headers()
        timeout = 14  # to finish graceful and absorb minor network outages, server shutdown is 15
        start = time.perf_counter()
        while 1:
            if radio in ghettoApi.radio_inst_dict.keys():
                if not ghettoApi.radio_inst_dict[radio].audio_out.empty():
                    start = time.perf_counter()  # reset
                    chunk = ghettoApi.radio_inst_dict[radio].audio_out.get()  # multiprocessor queue
                    self.wfile.write(chunk)
            idle = round((time.perf_counter() - start))
            if idle >= timeout:
                print(f'  HTTP Handler Thread - release connection {radio}')  # thread is no more locked and can go down
                break
            time.sleep(.1)

    @staticmethod
    def generate_index_html():
        """"""
        with open(os.path.join(dir_name, 'index.html'), 'r', encoding='utf-8') as f:
            while 1:
                line = f.readline()
                if line == '':
                    break
                yield line

    def get_index_html(self):
        """First call, we build the page. That's all.
        Button press on page will ajax 'do_POST' and update page.
        Ajax feed radio name, 'do_POST' calls py func and updates page.
        Java has to update the audio control element with new source URL (ghetto_simple stream srv on port 124....).

        :params: _o__radio_names____: write two radio buttons for a radio, stop (-) radio and run with to listen radio
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        generator = self.generate_index_html()
        while 1:
            try:
                next_line = next(generator)
                if '_o__gr_sky____' in next_line:
                    next_line = f"<img src='data:image/svg+xml;base64,{convert_img('gr_sky.svg')}'/>"
                if '_o__gr_basket____' in next_line:
                    next_line = f"<img src='data:image/svg+xml;base64,{convert_img('gr_sky_basket.svg')}'/>"
                if '_o__radio_names____' in next_line:
                    self.wfile.write(bytes("<div>stop 🌺 listen</div>", "utf-8"))
                    for radio_name in entry.config_file_radio_url_dict.keys():
                        radio_names_line = f"<div class='divRadioBtn' id='div{radio_name}'>" \
                                           "<label><input type='radio' name='da' " \
                                           f"id='-{radio_name}' onclick=ajax_switch_radio(id)></label>&nbsp; " \
                                           "<label><input type='radio' name='da' " \
                                           f"id='{radio_name}' onclick=ajax_switch_radio(id)>{radio_name}</label>" \
                                           "</div> "
                        self.wfile.write(bytes(radio_names_line, "utf-8"))
                    continue

            except StopIteration:  # last line already send, break in get_content()
                break
            self.wfile.write(bytes(next_line, "utf-8"))


def wait_shutdown():
    """"""
    return {'wait_shutdown': 'alive'}


def server_shutdown():
    """"""
    radio_lst = procenv.radio_instances_get()
    for radio in radio_lst:
        procenv.del_radio_instance(radio)
    helper.server_shutdown = True
    return {'server_shutdown': ' recorder_shutdown_init [20s]'}


def radio_title_get(radio):
    """Active radio interval title request."""
    title = procenv.radio_attribute_get(radio=radio, attribute='new_title')
    return {'title': title}


def switch_local_buffer(radio):
    """Radio checked if exists.
    Server checked by port number add digit (radio index in radio list) if exists already.
    """
    helper.content_type = None
    is_alive = True

    if radio == '0':  # disable cover div
        radio_instance_lst = procenv.radio_instances_get()
    elif radio[:1] == '-':  # del radio, name has a leading minus
        procenv.del_radio_instance(radio[1:])
        radio_instance_lst = procenv.radio_instances_get()
    else:  # add radio
        url = entry.config_file_radio_url_dict[radio]

        is_alive = procenv.radio_instance_create(radio, url, **entry.__dict__)
        radio_instance_lst = procenv.radio_instances_get()
    rv_dct = procenv.user_display_dict_get(radio)
    helper.content_type = rv_dct['content']
    rv_dct['recorder'] = radio_instance_lst
    if not is_alive:
        print('----------- fail -------------')
        rv_dct['content'] = 'no_response'
    return rv_dct


def start_radio_if_off(name, url):
    """feed content type to helper instance.
    create, fire and forget if error

    :returns: list of started radio instances names
    """
    is_online = procenv.radio_instance_create(name, url)
    active_radios_lst = procenv.radio_instances_get()
    if is_online:
        helper.content_type = procenv.radio_attribute_get(name, 'content_type')
    return active_radios_lst if is_online else False


def convert_img(file_name):
    """"""
    file_path = os.path.join(dir_name, 'static', 'images', file_name)
    base_64_str = utils.convert_ascii(file_path)
    return base_64_str


def read_config_file():
    """Ajax send content of config file settings.ini"""
    file = entry.config_name
    folder = entry.dir_name
    conf_path = os.path.join(folder, file)
    with open(conf_path, 'r', encoding='utf-8') as reader:
        file_cont = reader.read()
    return {'get_config_file': file_cont, 'path': conf_path}


def write_config_file(file_content):
    """
    """
    file = entry.config_name
    folder = entry.radios_parent_dir
    conf_path = os.path.join(folder, file)
    with open(conf_path, 'w', encoding='utf-8') as writer:
        writer.write(file_content)
    return {'write_config_file': 'Done: ' + str(time.ctime())}


def read_blacklist_file():
    """Ajax send content of config file settings.ini"""
    file = entry.blacklist_name
    folder = entry.radios_parent_dir
    file_path = os.path.join(folder, file)
    with open(file_path, 'r', encoding='utf-8') as reader:
        file_cont = reader.read()
    return {'get_blacklist_file': file_cont, 'path': file_path}


def write_blacklist_file(file_content):
    """
    """
    file = entry.blacklist_name
    folder = entry.radios_parent_dir
    file_path = os.path.join(folder, file)
    with open(file_path, 'w', encoding='utf-8') as writer:
        writer.write(file_content)
    return {'write_blacklist_file': 'Done: ' + str(time.ctime())}


# Create ONE socket.
addr = ('', 1242)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(addr)
sock.listen(5)


# Launch listener threads.
class Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        httpd = HTTPServer(addr, Handler, False)

        # Prevent the HTTP server from re-binding every handler.
        # https://stackoverflow.com/questions/46210672/
        httpd.socket = sock
        httpd.server_bind = self.server_close = lambda self: None

        httpd.serve_forever()


def main():
    """"""
    cmd.init()  # config file to api
    menu.record()  # ini to internal dict
    entry.config_file_radio_url_dict = menu.settings_ini_to_dict()  # our instance to work with
    for radio in entry.config_file_radio_url_dict.keys():
        entry.radio_name_list.append(radio)
    entry.config_file_settings_dict = menu.settings_ini_global()  # ini section [GLOBAL]
    entry.radio_selection_dict = menu.radio_url_dict_create()

    remote_dir = ghettoApi.path.save_to_dir  # terminal menu option, not the default in [GLOBAL] from settings.ini
    if remote_dir:
        entry.radios_parent_dir = pathlib.Path(ghettoApi.path.save_to_dir)
    else:
        entry.radios_parent_dir = pathlib.Path(ghettoApi.path.config_dir)

    cmd.show_radios_urls_formatted()
    cmd.ghetto_blacklist.init(**entry.__dict__)

    [Thread() for _ in range(3)]  # all on same port, means if range(2) one can connect 2 browser tabs = 2 connections
    print("\n\tUser Interface at " + "http://localhost:1242/")

    while 1:  # keep the show running
        time.sleep(1)
        if helper.server_shutdown:
            ghettoApi.blacklist.stop_blacklist_writer = True
            time.sleep(15)  # wait timeout listen handler on audio_out queue
            break   # Process finished with exit code 0, if all threads are down
        # names_list = [thread.name for thread in threading.enumerate()]
        # print(names_list)


if __name__ == '__main__':
    main()

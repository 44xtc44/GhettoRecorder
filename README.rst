Documentation - GhettoRecorder
==============================
![alt logo of ghettorecorder](https://github.com/44xtc44/ghettorecorder/raw/dev/docs/source/_static/ghetto_url.svg)
Grab hundreds of radio stations `simultaneously`.

How to run installed package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
GhettoRecorder
class module (example in ghetto_procenv).::

    from ghettorecorder import GhettoRecorder

    ghetto_01 = GhettoRecorder(radio, url)
    ghetto_01.com_in = mp.Queue(maxsize=1)  # eval exec communication for multiprocessing
    ghetto_01.audio_out = mp.Queue(maxsize=1)  # can also be normal queue.Queue()

Commandline
option (calls cmd.py).::

    ghetto_cmd or
    python3 -m ghettorecorder.cmd

Client Server
option (calls __main__.py).::

    ghetto_url or
    python3 -m ghettorecorder

Overview
~~~~~~~~~
* Queue communication. Multiprocessor ready.
* GhettoRecorder class has connector attributes for external modules.
* External modul *Blacklisting recorded titles* is already included.
* Optional Browser Frontend on Python multithreading HTTP server.

Links
~~~~~
* Snap: https://snapcraft.io/ghettorecorder
* GitHub: https://github.com/44xtc44/GhettoRecorder
* Issues to fix: https://github.com/44xtc44/GhettoRecorder/issues
* ReadTheDocs: https://ghettorecorder.readthedocs.io/ (see module index)

Configuration File
------------------
'Settings.ini' is the config file for GhettoRecorder.
INI files consist of sections to divide different settings.::

    [STATIONS]
    anime_jp = http://streamingv2.shoutcast.com/japanimradio-tokyo

    [GLOBAL]
    blacklist_enable = True
    save_to_dir = f:\54321


| [STATIONS]
| custom radio name and radio connection information (can be pls or m3u playlist)

| [GLOBAL]
| stores blacklist status and the *custom* parent directory location

Usage
-----
Main Menu
^^^^^^^^^
::

    menu 'Main'
    1 -- Record (local listen option)
    2 -- Change parent record path
    3 -- Enable/disable blacklists
    4 -- Set path to config, settings.ini
    5 -- aac file repair
    6 -- Exit


Record Menu
^^^^^^^^^^^
::

    0 	>> aacchill             <<
    1 	>> 80ies_nl             <<
    2 	>> anime_jp             <<
    3 	>> blues_uk             <<
    4 	>> br24                 <<
    ...
    Enter to record -->:

| Write the leading Number (list index) into the input field . Hit 'Enter'.
| OR
| Write or copy/paste the radio name into the input field. Hit 'Enter'.
| Add as many radios as you like.
| Hit 'Enter' without input to start grabbing.
| Listen to the first selected radio via local streaming ``http://localhost:1242/``

Change parent record path Menu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    option 'Change record parent path'
    1 -- New parent path for recorded radios. Write to config.
    2 -- Back to Main Menu
    Enter your choice: 1

        Write a new path to store files
    ..settings.ini [GLOBAL] section: {'blacklist_enable': 'True', 'save_to_dir': 'f:\\31'}
    Enter a new path, OS syntax (f:\10 or /home ) -->:

The default path is the directory of the module.
In most cases you want to store grabbed files somewhere else.

Blacklist Menu
^^^^^^^^^^^^^^
::

    Write a new blacklist option to settings.ini file
    ..settings.ini [GLOBAL] section: {'blacklist_enable': 'True', 'save_to_dir': 'f:\\31'}
    1 -- blacklist on (don't write title if already downloaded)
    2 -- blacklist off
    3 -- Back to Main Menu
    Enter your choice: 1

    	blacklist is ON: settings.ini file
    	Existing titles are not recorded again and again.
    file name is "blacklist.json" in the same folder as "settings.ini"
    ..settings.ini [GLOBAL] section: {'blacklist_enable': 'True', 'save_to_dir': 'f:\\31'}
    Hit Enter to leave -->:

| Blacklist writing can be switched on/off.
| Titles are listed for each of the radios and can be deleted to 'unlist' them.
| File name is ``blacklist.json`` and always in the same folder as 'settings.ini'.


Set path to config
^^^^^^^^^^^^^^^^^^
::

    Write Path to settings.ini and blacklist.json file
    Enter a new path, OS syntax (f:\10 or /home ) -->: F:\44
    	created: F:\44
    ..settings.ini [GLOBAL] section: {'blacklist_enable': 'True'}
    Hit Enter to leave -->:

| You can store your config file 'settings.ini' somewhere on the file system.
| Default place for grabbed files is the mentioned folder.
| If a custom save path is written to config, this path is used.


aac file repair
^^^^^^^^^^^^^^^
::

    Write a path to aac files. Only aac files will be touched.
    ..settings.ini [GLOBAL] section: {'blacklist_enable': 'True', 'save_to_dir': 'f:\\31'}
    Enter a path, OS syntax (f:\10 or /home ) -->:f:\6aac
    	created: f:\6aac
    	f:\6aac\aac_repair created
    [ COPY(s) in f:\6aac\aac_repair ]
    ----- 1 file(s) failed -----
    f:\6aac\Sergey Sirotin & Golden Light Orchestra - Around The World.aacp
    ValueError non-hexadecimal number found in fromhex() arg at position 5438113
    ----- 97 file(s) repaired -----
    f:\6aac\111_Slovo_Original_Mix.aac; cut(bytes): [330]
    f:\6aac\351 Lake Shore Drive - You Make My Day.aacp; cut(bytes): [389]

| The repair option uses a folder name as input.
| Repaired files are stored in 'aac_repair' sub folder.
| Cut bytes count is shown at the end of the line.
| Repair can fail if the file is corrupted not only at start or end.


Pip Install
^^^^^^^^^^^
::

   """ Linux """
   $ pip3 install ghettorecorder

   """ Windows """
   > pip install ghettorecorder


Uninstall
^^^^^^^^^

Python user

 * find the module location
 * uninstall and then remove remnants

remove::

   >$ pip3 show ghettorecorder
   >$ pip3 uninstall ghettorecorder

Location: ... /python310/site-packages

GhettoRecorder module
~~~~~~~~~~~~~~~~~~~~~~
Communication with the GhettoRecorder instance

       ========= ================= ======================================================
       port      action            description
       ========= ================= ======================================================
       com_in    commands input    tuple (radio, [str 'eval' or 'exec'], str 'command')
       com_out   status, err msg   (radio, [str 'eval' or 'exec'], response)
       audio_out copy of html resp server can loop through to a browser
       ========= ================= ======================================================

Feature attributes to switch on/off

       ========================== ==================================================================================
       attribute                  description
       ========================== ==================================================================================
       runs_meta                  call metadata periodically, create path for rec out; False: recorder is the file
       runs_record                disable writing to recorder file at all
       recorder_file_write        allow dumping current recorder file
       runs_listen                disable write to audio output queue; 3rd party can grab it. (listen blacklist)
       ========================== ==================================================================================

Snapcraft package
~~~~~~~~~~~~~~~~~~
The installer creates an icon with the name "GhettoRecorder".
You can use two command line options.::

    ghettorecorder.url
    ghettorecorder.cmd

First is Client, Server connection.
Second is command line menu.

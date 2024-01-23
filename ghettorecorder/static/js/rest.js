// rest.js
"use strict";


function ajax_switch_radio(radio_btn_id) {
  /**
   * AJAX - radio btn press start recorder and or audio element in browser.
   * radio_btn_id is actually the name of the radio,
   *   it has a minus before the name if it is removed (stop)
   */
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/radio_btn_id');

  xhr.onload = function () {
    console.log('xhr r ', xhr.response);
    var data = JSON.parse(xhr.responseText);
    console.log('resp r ', data.content);
    // response from stop request, dict all null, except radio_name is: -randio
    if (!data.radio_dir) {
      // set var for interval title scan
      glob.playingRadio = false;
    }
    /* radio buttons */
    let divRadioBtn = document.getElementsByClassName('divRadioBtn');
    // set all uniform
    for (var i = 0; i < divRadioBtn.length; i++) {
      divRadioBtn[i].style.color = '#000000';
      divRadioBtn[i].style.backgroundColor = '#f9f9f9ff';
    }
    // adapt recorder active buttons
    for (const elem of data.recorder) {
      let rec = document.getElementById('div' + elem);
      rec.style.color = '#f9f9f9ff';
      rec.style.backgroundColor = '#fd7f7f';
    }
    /* bottom page footer */
    let pMsg = document.getElementById('pMsg');
    pMsg.innerHTML = '';
    pMsg.innerHTML = xhr.response;
    pMsg.style.backgroundColor = '#cf4d35ff';
    pMsg.style.fontFamily = 'PT Sans, arial';
    pMsg.style.padding = '10px'; pMsg.style.color = '#f9f9f9ff';
    /* radio shall run but is not responding */
    if (data.content == "no_response") {
      console.log('no_response ', data.radio_name);
      let radio = document.getElementById("div" + data.radio_name);
      radio.style.backgroundColor = 'black';
      return;
    }
    /* enable sound */
    let audioR = document.getElementById('audioR');
    // stopped radio btn has (-) a minus in front of the name
    if (data.radio_name == radio_btn_id) {  // data.radio_name is ajax return value
      audioR.src = 'http://localhost:' + data.server_port + '/sound/' + data.radio_name;
      let playPromise = audioR.play();    // must check status, else DOM promise error in log
      if (playPromise !== undefined) {
        playPromise.then(function () {
          // "Automatic playback started!"
        }).catch(function (error) {
          // "Automatic playback failed."
        });
      }
      // set var for interval title scan
      glob.playingRadio = data.radio_name;
    }
  };
  xhr.send(radio_btn_id);
}
;
function ajax_title_get() {
  /**
   * AJAX - active radio title display.
   */
  console.log('glob.playingRadio ', glob.playingRadio);
  if (!glob.playingRadio) { return; }
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/title_get');

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    console.log('resp t ', data.title);
    if (!data.title) { return; }
    let pTitle = document.getElementById('pTitle');
    pTitle.style.fontFamily = 'PT Sans, arial'; pTitle.style.padding = '10px';
    pTitle.innerHTML = ''; pTitle.innerHTML = '[' + glob.playingRadio + '] ' + data.title;
  };
  xhr.send(glob.playingRadio);
}
;
function ajax_get_config_file() {
  /**
   * AJAX - settings.ini file in cheapo 'editor' mode.
   */
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/get_config_file');

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    console.log('resp gc ', data);
    let configFileEdit = document.getElementById('configFileEdit');
    configFileEdit.value = data.get_config_file;
    // write path of file
    let configFileEditPath = document.getElementById('configFileEditPath');
    configFileEditPath.innerHTML = data.path;
    configFileEditPath.style.backgroundColor = '#fd7f7f';
  };
  xhr.send(null);
}
;
function ajax_write_config_file() {
  /**
   * AJAX - settings.ini file send back to file system.
   */
  let configFileEdit = document.getElementById('configFileEdit');
  var configContent = configFileEdit.value;

  const xhr = new XMLHttpRequest();

  xhr.open('POST', '/write_config_file');
  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    console.log('resp wc ', data.write_config_file);

    let pConfigResponse = document.getElementById('pConfigResponse');
    pConfigResponse.innerHTML = data.write_config_file;
  };
  xhr.send(configContent);
}
;
function ajax_get_blacklist_file() {
  /**
   * AJAX - blacklist.json file in cheapo 'editor' mode.
   */
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/get_blacklist_file');

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    // console.log('resp gb ', data);
    let blacklistFileEdit = document.getElementById('blacklistFileEdit');
    blacklistFileEdit.value = data.get_blacklist_file;
    // write path of file
    let blacklistFileEditPath = document.getElementById('blacklistFileEditPath');
    blacklistFileEditPath.innerHTML = data.path;
    blacklistFileEditPath.style.backgroundColor = '#fd7f7f';
  };
  xhr.send(null);
}
;
function ajax_write_blacklist_file() {
  /**
   * AJAX - blacklist.json file send back to file system.
   */
  let blacklistFileEdit = document.getElementById('blacklistFileEdit');
  var blacklistContent = blacklistFileEdit.value;

  const xhr = new XMLHttpRequest();

  xhr.open('POST', '/write_blacklist_file');
  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    // console.log('resp wb ', data.write_blacklist_file);

    let pBlacklistResponse = document.getElementById('pBlacklistResponse');
    pBlacklistResponse.innerHTML = data.write_blacklist_file;
  };
  xhr.send(blacklistContent);
}
;
function ajax_server_shutdown() {
  /**
   * AJAX - recorder shut down via server call.
   */
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/server_shutdown');

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    console.log('resp ss ', data.server_shutdown);

    let pMsg = document.getElementById('pMsg');
    let sMsgShutDown = document.getElementById('sMsgShutDown');
    pMsg.innerHTML = '';
    pMsg.innerHTML = data.server_shutdown;
    sMsgShutDown.style.backgroundColor = 'lightGreen';
    sMsgShutDown.innerHTML = data.server_shutdown;
    glob.waitShutdownIntervalId = setInterval(ajax_wait_shutdown, 2500);
  };
  xhr.send();
}
;
function ajax_wait_shutdown() {
  /**
   * AJAX - Show the current shut down status.
   */
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/wait_shutdown');
  xhr.timeout = 2000;

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);
    console.log('resp ws ', data.wait_shutdown);

    let pMsg = document.getElementById('pMsg');
    let sMsgShutDown = document.getElementById('sMsgShutDown');

    pMsg.innerHTML = '';
    pMsg.innerHTML = data.wait_shutdown;
    sMsgShutDown.style.backgroundColor = 'lightYellow';
    sMsgShutDown.innerHTML = data.wait_shutdown;
  };
  xhr.ontimeout = function (e) {
    // request timed out
    pMsg.innerHTML = '';
    pMsg.innerHTML = 'down';

    sMsgShutDown.style.backgroundColor = '#fd7f7f';
    sMsgShutDown.innerHTML = '';
    sMsgShutDown.innerHTML = 'down';
    // disable setInterval
    clearInterval(glob.waitShutdownIntervalId);
  };
  xhr.send();
}
;

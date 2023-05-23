/**
*  - GhettoRecorder is not only an App
*  - GhettoRecorder provides an interface you can connect to
*  - develop modules to enhance functionality like the (free) delivered blacklist module
*  - (A) write your own module to record on demand, if a metadata string matches your table content
*  - (B) write a listen blacklist module and temporary play local audio files instead
*  - (C) write a module that dynamically loads only radios of a certain genre or country to serve your hotel guests
*  - Your module can switch GhettoRecorder features on/off
*  - provides Python features to switch and read: metadata, record write, listen, response header attributes
*  - provides Python interfaces to connect to: com_in, com_out, audio_out,
*
* This is a JS mini frontend.
* Showcase: Basic Browser Web audio interface with Python HTTP server to visualize and manipulate network sound.
*   This is only possible due to the local server, where we circumvent the Browser CORS restrictions.
* You can deliver a whole multimedia animated show with svg, video, cartoons, 3d plot, blender ... to sell your product.
*/
var nameRadioPlays = false;  // (browser audio element) <- (http server method loop) <- (py instance.audio_out queue)
var waitShutdownIntervalId = 0;  // get internal id of setInterval to disable setInterval(ajax_wait_shutdown, 2500);

window.addEventListener('load', function() {
    /**
     * Html loaded, can get id and class.
     */
    console.log('All assets are loaded');
    const audioR = document.getElementById('audioR');
    const gainR = document.getElementById('gainR');
    gainR.addEventListener("input", setAudioGain);  // move slider of gain
    setInterval(ajax_title_get, 30000);
    const canvasBalloon = document.getElementById('canvasBalloon');
})

class HiddenOnOff{
    /**
     * Switch the visibility of an element on/off. Javascript has no Py getattr, setattr. We save elem names as key.
     * Overkill for one or two divs, but becomes handy for reuse.
     * Use:
     *  init at the bottom of this script
     *  hiddenOnOff = new HiddenOnOff()
     *  hiddenOnOff.update({element:'divControllerSlider', set:false})
     *  hiddenOnOff.toggle({element:'divControllerSlider'})
     */
  constructor() {
    // initial div values if page is loaded
    this.isSwitchedOn = {};
    this.isSwitchedOn['divOverlay'] = false;  // remove page cover to enable audio element in browser
    this.isSwitchedOn['divEdit'] = false;  // show, hide div edit settings.ini
    this.isSwitchedOn['divControllerSlider'] = false;  // show, hide div edit volume and gain
    this.isSwitchedOn['divEditConfig'] = false;  // editor for settings.ini
    this.isSwitchedOn['divEditBlacklist'] = false;  // editor for blacklist.json
    this.isSwitchedOn['divBalloon'] = true;  // canvas balloon with basket
    // edit menu option p elements
    this.isSwitchedOn['pShutdown'] = true;
    this.isSwitchedOn['pDocu'] = true;
    this.isSwitchedOn['pEditConfig'] = true;
    this.isSwitchedOn['pEditBlacklist'] = true;
  };
  update(options) {
    // set explicit
    if(options === undefined) alert('HiddenOnOff update no options');  // just show how this options guy is working
    if(options.element === undefined) alert('HiddenOnOff update no element');
    let obj = document.getElementById(options.element);

    if (options.set) {
      obj.style.display = 'inline-block';
      this.isSwitchedOn[options.element] = true;
    } else {
      obj.style.display = 'none';
      this.isSwitchedOn[options.element] = false;
    }
  };
  toggle(options) {
    if(options.element === undefined) alert('HiddenOnOff update no element');
    let obj = document.getElementById(options.element);

    if (!this.isSwitchedOn[options.element]) {
      obj.style.display = 'inline-block';  // toggle
      this.isSwitchedOn[options.element] = true;  // toggle
    } else {
      obj.style.display = 'none';
      this.isSwitchedOn[options.element] = false;
    }
  };
}
;
function audioEnable () {
    /**
     * User interaction required to enable audio context.
     */
    setAudioContextVisual();
    draw();  // animate.js
}
;
function setAudioContextVisual() {
    /**
     * Create audio nodes and connect them.
     */
    audioContext = new AudioContext();
    gainNode = audioContext.createGain();
    analyserNode = audioContext.createAnalyser();
    audioSource = audioContext.createMediaElementSource(audioR);
    audioSource.connect(analyserNode).connect(gainNode).connect(audioContext.destination);
}
;
function setAudioGain() {
    /**
     * Gain controller value input if slider in action.
     */
    gainNode.gain.value = gainR.value;
}
;
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
        console.log('resp r ', data.content, data.port);
        if (data.radio_name) {nameRadioPlays = data.radio_name;};

          let divRadioBtn=document.getElementsByClassName('divRadioBtn');  /* radio buttons */
          for(var i = 0; i < divRadioBtn.length; i++){
            divRadioBtn[i].style.backgroundColor = '#f9f9f9ff'; divRadioBtn[i].style.color = 'brown';
          }
          for (const elem of data.recorder) {
            let rec=document.getElementById('div' + elem);
            rec.style.color='#f9f9f9ff'; rec.style.backgroundColor='#fd7f7f';
          }
          let pMsg=document.getElementById('pMsg');  /* bottom page footer */
          pMsg.innerHTML='';
          pMsg.innerHTML=xhr.response;
          pMsg.style.backgroundColor='#cf4d35ff';
          pMsg.style.fontFamily='PT Sans, arial';
          pMsg.style.padding='10px';pMsg.style.color='#f9f9f9ff';

        if (data.content == "no_response") {  /* radio shall run but is not responding */
          console.log('no_response ', data.radio_name);
          let radio = document.getElementById("div" + data.radio_name);
          radio.style.backgroundColor='black';
          return;
        }
        if (data.radio_name == null) {return;}  /* other radio removed, returned dict is empty, Null*/
          /* enable sound */
          let audioR = document.getElementById('audioR'); console.log('srv', 'http://localhost:' + data.port);
          nameRadioPlays=data.radio_name; console.log('nameRadioPlays ', nameRadioPlays);
          audioR.src='http://localhost:1242/sound/' + data.radio_name;
          audioR.load();audioR.play();
          nameRadioPlays = data.radio_name;
    };
    xhr.send(radio_btn_id);
}
;
function ajax_title_get() {
    /**
     * AJAX - active radio title display.
     */
    if (!nameRadioPlays) {return;}
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/title_get');

    xhr.onload = function () {
      var data = JSON.parse(xhr.responseText);
      console.log('resp t ', data.title);
      if (!data.title) {return;} /**/;
        let pTitle=document.getElementById('pTitle');
        pTitle.style.fontFamily='PT Sans, arial';pTitle.style.padding='10px';
        pTitle.innerHTML=''; pTitle.innerHTML= '[' + nameRadioPlays + '] ' + data.title;
    };
    xhr.send(nameRadioPlays);
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
      pConfigResponse.innerHTML= data.write_config_file;
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
      pBlacklistResponse.innerHTML= data.write_blacklist_file;
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
      waitShutdownIntervalId = setInterval(ajax_wait_shutdown, 2500);
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
        clearInterval(waitShutdownIntervalId);
    };
    xhr.send();
}
;

/* init class */
hiddenOnOff = new HiddenOnOff()
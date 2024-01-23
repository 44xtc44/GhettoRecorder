// index.js  https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html
"use strict";

/**
* Basic Browser Web audio interface with Python HTTP server to visualize and manipulate network sound.
* Vanilla JS in this project!
*/

const requestAnimationFrame =
  window.requestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.msRequestAnimationFrame;
const cancelAnimationFrame =
  window.cancelAnimationFrame || window.mozCancelAnimationFrame;
const cl = console.log

window.addEventListener('load', function () {
  /**
   * Html loaded, can get id and class now.
   */
  cl('All assets are loaded');
  document.body.style.overflowX = "hidden";  // get rid of x scroll bar at bottom
  const audioR = document.getElementById('audioR');
  const gainR = document.getElementById('gainR');
  gainR.addEventListener("input", setAudioGain);  // move slider of gain
  setInterval(ajax_title_get, 10000);
  const canvasBalloon = document.getElementById('canvasBalloon');
  window.glob = new Glob();
  glob.updateScreen();
  window.hiddenOnOff = new HiddenOnOff()
  // Gather all elements in the draggable-div class into a collection
  let draggable = document.querySelectorAll(".draggable-div");
  draggable.forEach(function (el) {
    dragElement(el);  // animate.js
    touchMoveMobile(el)  // animate.js
  });
})
  ;

class Glob {
  /* *
   * global variables container and base functions resort
   */
  constructor() {
    this.playingRadio = false; // (browser audio element) <- (http server method loop) <- (py instance.audio_out queue)
    this.waitShutdownIntervalId = 0;  // store id of setInterval to disable setInterval(ajax_wait_shutdown, 2500);
    this.animationRuns = 0;  // toggle animations
    this.animationRunsMax = 1;  // Max animation callAnimation() can switch 0,1,2
    this.windowWidth = window.innerWidth;
  }
  numberRange(start, end) {  // simulate range() of Python
    return new Array(end - start).fill().map((d, i) => i + start);
  }
  // return a random integer
  getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
  updateScreen() {
    // called by checkWindowWidth(); rearrange for mobiles small screens
    let divAirOne = document.getElementById('divAirOne');
    let spanHeaderCenter = document.getElementById('spanHeaderCenter');
    spanHeaderCenter
    if (this.windowWidth <= 1080) {
      divAirOne.style.top = "26em";
      divAirOne.style.left = "2.0em";
      spanHeaderCenter.innerHTML = "Ghetto";
    } else {
      divAirOne.style.top = "14em";
      divAirOne.style.left = "2.0em";
      spanHeaderCenter.innerHTML = "GhettoRecorder";
    }
  }
  toggleAnimation() {
    this.animationRuns += 1;
    if (this.animationRuns > this.animationRunsMax) { this.animationRuns = 0; }
  }
}
;

function checkWindowWidth() {
  glob.windowWidth = window.innerWidth;
  glob.updateScreen();
}
;
window.addEventListener('resize', checkWindowWidth);


class HiddenOnOff {
  /** End the miserable behavior of asking for display attribute and get back bullsh*t. Result in "must" double click.
   * Switch the visibility of an element on/off. Javascript has no Py getattr, setattr. We save elem names as key.
   * Overkill for one or two divs, but becomes handy for reuse.
   * Reading the display status leads often to switch pb. e.g. double click to hide. We save status in vars.
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

    // Airplane
    this.isSwitchedOn['svgAirOne'] = true;
  };
  update(options) {
    // set action explicit
    if (options === undefined) alert('HiddenOnOff update no options');  // just show how this options guy is working
    if (options.element === undefined) alert('HiddenOnOff update no element');
    let obj = document.getElementById(options.element);

    if (options.set) {
      obj.style.display = 'inline-block';
      this.isSwitchedOn[options.element] = true;
    } else {
      obj.style.display = 'none';
      this.isSwitchedOn[options.element] = false;
    }
  }
  toggle(options) {
    if (options.element === undefined) alert('HiddenOnOff update no element');
    let obj = document.getElementById(options.element);

    if (!this.isSwitchedOn[options.element]) {
      obj.style.display = 'inline-block';  // toggle
      this.isSwitchedOn[options.element] = true;  // toggle
    } else {
      obj.style.display = 'none';
      this.isSwitchedOn[options.element] = false;
    }
  }
}


function audioEnable() {
  /** in INDEX.HTML, overlay div click enables audio
   * User interaction required to enable audio context.

   * Switch on animations.
   */
  setAudioContextVisual();
  enableAirplane();
  callAnimation();
}
;

function setAudioContextVisual() {
  /**
   * Create audio nodes and connect them.
   */
  window.audioContext = new AudioContext();  // instance IS same as audioR, but then we must use JS to apply controls
  window.gainNode = audioContext.createGain();
  window.analyserNode = audioContext.createAnalyser();
  window.audioSource = audioContext.createMediaElementSource(audioR);  // audioR elem defined in index.html to show controls
  // connect audio network client of index.html with analyser, with gain control and then with computer speaker
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

// index.js
"use strict";
/**
* @fileoverview Entry point for JS. See how TS helps in real world.
* <p>Browser Web audio interface to Python HTTP server. Visualize and manipulate network sound.</p>
* <p>Vanilla JS in V3.0 of this project! Fully functional, no errors.</p>
* <p>Ported incremental to Typescript. Errors due to limitations of Typescript.</p>
* @author René Horn
* @author www.github.com/44xtc44
* @version 3.0
* @since 1.0
* @see license MIT
*/
const cl = console.log;
window.addEventListener('load', function () {
    document.body.style.overflowX = "hidden"; // get rid of x scroll bar at bottom
    setInterval(ajax_title_get, 10000);
    glob.updateScreen();
    // Gather all elements in the draggable-div class into a collection
    let draggable = document.querySelectorAll(".draggable-div");
    for (let i = 0; i <= draggable.length - 1; i++) {
        touchMoveMobile(draggable[i]);
        dragMoveMouse(draggable[i]);
    }
    ;
});
class Glob {
    /* *
     * global variables container and base functions resort
     * @playingRadio  - (browser audio element) <- (http server method loop) <- (py instance.audio_out queue)
     * @waitShutdownIntervalId - store id of setInterval to disable setInterval(ajax_wait_shutdown, 2500);
     * @animationRuns - toggle animations
     * @animationRunsMax - Max animation callAnimation() can switch 0,1,2
     * @windowWidth - width in number of px
     */
    constructor(playingRadio = false, waitShutdownIntervalId = 0, animationRuns = 0, animationRunsMax = 1, windowWidth = window.innerWidth) {
        this.playingRadio = playingRadio;
        this.waitShutdownIntervalId = waitShutdownIntervalId;
        this.animationRuns = animationRuns;
        this.animationRunsMax = animationRunsMax;
        this.windowWidth = windowWidth;
    }
    numberRange(start, end) {
        return new Array(end - start).fill(undefined).map((d, i) => i + start);
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
        if (this.windowWidth <= 1080) {
            if (divAirOne !== null)
                divAirOne.style.top = "26em";
            if (divAirOne !== null)
                divAirOne.style.left = "2.0em";
            if (spanHeaderCenter !== null)
                spanHeaderCenter.innerHTML = "Ghetto";
        }
        else {
            if (divAirOne !== null)
                divAirOne.style.top = "14em";
            if (divAirOne !== null)
                divAirOne.style.left = "2.0em";
            if (spanHeaderCenter !== null)
                spanHeaderCenter.innerHTML = "GhettoRecorder";
        }
    }
    toggleAnimation() {
        this.animationRuns += 1;
        if (this.animationRuns > this.animationRunsMax) {
            this.animationRuns = 0;
        }
    }
}
;
const glob = new Glob();
function checkWindowWidth() {
    glob.windowWidth = window.innerWidth;
    glob.updateScreen();
}
;
window.addEventListener('resize', checkWindowWidth);
class HiddenOnOff {
    /**
     * Switch the visibility of an element on/off. Javascript has no Py getattr, setattr. We save elem names as key.
     * Overkill for one or two divs, but becomes handy for reuse.
     * Reading the display status leads often to switch pb. e.g. double click to hide. We save status in vars.
     * Use:
     *  init at the bottom of this script
     *  hiddenOnOff = new HiddenOnOff()
     *  hiddenOnOff.update({element:'divControllerSlider', set:false})
     *  hiddenOnOff.toggle({element:'divControllerSlider'})
     */
    constructor(isSwitchedOn = {
        // initial div values if page is loaded
        'divOverlay': false, // remove page cover to enable audio element in browser
        'divEdit': false, // show, hide div edit settings.ini
        'divControllerSlider': false, // show, hide div edit volume and gain
        'divEditConfig': false, // editor for settings.ini
        'divEditBlacklist': false, // editor for blacklist.json
        'divBalloon': true, // canvas balloon with basket
        // edit menu option p elements
        'pShutdown': true,
        'pDocu': true,
        'pEditConfig': true,
        'pEditBlacklist': true,
        // Airplane
        'svgAirOne': true
    }) {
        this.isSwitchedOn = isSwitchedOn;
    }
    ;
    update(options) {
        // set action explicit, regardless of current status
        let elem = document.getElementById(options.element);
        if (options.set) {
            if (elem !== null)
                elem.style.display = 'inline-block';
            this.isSwitchedOn[options.element] = true;
        }
        else {
            if (elem !== null)
                elem.style.display = 'none';
            this.isSwitchedOn[options.element] = false;
        }
    }
    toggle(options) {
        let elem = document.getElementById(options.element);
        if (!this.isSwitchedOn[options.element]) {
            if (elem !== null)
                elem.style.display = 'inline-block'; // toggle
            this.isSwitchedOn[options.element] = true; // toggle
        }
        else {
            if (elem !== null)
                elem.style.display = 'none';
            this.isSwitchedOn[options.element] = false;
        }
    }
}
const hiddenOnOff = new HiddenOnOff();
function audioEnable() {
    /**
     * overlay div click enables audio
     * User interaction required to enable audio context.
     * Switch on animations.
     */
    audioContextCreate.init();
    enableAirplane();
    callAnimation();
}
;
class AudioContextCreate {
    /**
     * The point is here to avoid the error msg AudioContext was hindered to play automatically.
     * Need to expose ``analyzerNode`` for spectrum analyzer show on canvas.
     * Declare an empty instance at first. Init after user interaction and DOM has all elements loaded.
     */
    constructor(audioContext = null, gainNode = null, analyserNode = null, audioR = null, gainR = null, audioSource = null) {
        this.audioContext = audioContext;
        this.gainNode = gainNode;
        this.analyserNode = analyserNode;
        this.audioR = audioR;
        this.gainR = gainR;
        this.audioSource = audioSource;
    }
    init() {
        /**
         * Init AFTER user interaction.
         * Must connect HTMLElement late, but consumer fun auto init at startup.
         */
        this.audioContext = new AudioContext(),
            this.gainNode = this.audioContext.createGain(),
            this.analyserNode = this.audioContext.createAnalyser(),
            this.audioSource, // audioR recorder in index.html connector, TS typed def for AudioContext not working
            this.audioR = document.getElementById('audioR'),
            this.audioSource = this.audioContext.createMediaElementSource(this.audioR), // audioR elem defined in index.html to show controls
            this.gainR = document.getElementById('gainR'),
            // connect audio network client of index.html with analyser, with gain control and then with computer speaker
            this.audioSource.connect(this.analyserNode).connect(this.gainNode).connect(this.audioContext.destination);
        if (this.gainR !== null)
            this.gainR.addEventListener("input", (e) => {
                /**
                 * Gain controller raise/lower input value if slider in action.
                 * Typescript complains gainR.value is a string.
                 */
                if (this.gainNode !== null && this.gainR !== null)
                    this.gainNode.gain.value = parseInt(this.gainR.value);
            });
    }
}
const audioContextCreate = new AudioContextCreate();

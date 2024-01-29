// animate.js
"use strict";

var frameCount = 0;

/**
* @fileoverview Call animations per browser frame and provide drag and drop.
* Single fun to call all animations.
* index.html switch spectrum analyzer <code>onclick="glob.toggleAnimation();"</code>
* index.html hide animatedAirplane() <code>onclick="hiddenOnOff.toggle({element:'svgAirOne'});"</code>
*/
function callAnimation() {
  if (glob.animationRuns === 0) {
    draw();
  } else if (glob.animationRuns === 1) {
    animatedBars();
  } else { }
  animatedAirplane();
  frameCount = requestAnimationFrame(callAnimation);
}
;
function dragMoveMouse(box: HTMLElement) {
  /* div draggable */
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  box.onmousedown = dragMouseDown;


  function dragMouseDown(e: MouseEvent) {
    e.preventDefault();
    // get the mouse cursor position at startup
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves
    document.onmousemove = elementDrag;
  }

  function elementDrag(e: MouseEvent) {
    e.preventDefault();
    // assign new coordinates based on the touch on the viewport .clientX
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position
    box.style.top = (box.offsetTop - pos2) + "px";
    box.style.left = (box.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released
    document.onmouseup = null;
    document.onmousemove = null;
  }
}
;

function touchMoveMobile(box: HTMLElement) {

  box.addEventListener('touchmove', (e) => {
    // grab the location of touch
    var touchLocation = e.targetTouches[0];

    // assign box new coordinates based on the touch.
    box.style.left = touchLocation.pageX + 'px';
    box.style.top = touchLocation.pageY + 'px';
  })

  /* record the position of the touch
  when released using touchend event.
  This will be the drop position. */

  box.addEventListener('touchend', function (e) {
    // current box position.
    var x = parseInt(box.style.left);
    var y = parseInt(box.style.top);
  })
}
;
// spectrumAnalyzer.js
"use strict";

/**
* Spectrum analyzer jumping horizontal lines.
*/
function draw() {
  let canvas = document.getElementById('canvasBalloon');
  let canvasCtx = canvas.getContext('2d');
  analyserNode.fftSize = 2048;
  const bufferLength = analyserNode.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);
  analyserNode.getByteTimeDomainData(dataArray);

  canvasCtx.clearRect(0, 0, canvas.width, canvas.height); // not if second anim in background
  canvasCtx.lineWidth = 2.0;

  const gradient = canvasCtx.createLinearGradient(canvas.width / 1.5, 0, canvas.width / 2, canvas.height);
  gradient.addColorStop(0, "lightYellow");
  gradient.addColorStop(1, "turquoise");
  canvasCtx.fillStyle = gradient; //'turquoise';

  canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
  canvasCtx.strokeStyle = 'red'; canvasCtx.beginPath();
  var sliceWidth = canvas.width * 1.0 / bufferLength; var x = 0;
  for (var i = 0; i < bufferLength; i++) {
    var v = dataArray[i] / 128.0;
    var y = v * canvas.height / 2;
    if (i === 0) { canvasCtx.moveTo(x, y); } else { canvasCtx.lineTo(x, y); }
    x += sliceWidth;
  }
  canvasCtx.stroke();
}
;
/**
* Spectrum analyzer retro equalizer style.
*/
function animatedBars() {
  let canvas = document.getElementById('canvasBalloon');
  let canvasCtx = canvas.getContext('2d');
  analyserNode.fftSize = 128;
  const bufferLength = analyserNode.frequencyBinCount;
  var barWidth = (canvas.width / bufferLength) * 2;
  const dataArray = new Uint8Array(bufferLength);
  analyserNode.getByteFrequencyData(dataArray);
  let x = 0 - barWidth * 2;
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);  // not if second anim in background

  for (let i = 0; i < bufferLength; i++) {
    let barHeight = ((dataArray[i] / 2) - 12) + 2;
    canvasCtx.lineWidth = 3;
    canvasCtx.fillStyle = 'red';
    canvasCtx.fillRect(x, canvas.height - barHeight - 3, barWidth, 3);
    canvasCtx.fillStyle = 'rgb(219, 111, 52)';
    canvasCtx.fillRect(x, canvas.height - barHeight - 6, barWidth, 3);
    canvasCtx.fillStyle = 'blue';
    canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    x += barWidth;
  }
}
;

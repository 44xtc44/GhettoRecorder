// spectrumAnalyzer.js
"use strict";

/**
* @fileoverview Spectrum analyzer shows on canvas.
* Spectrum analyzer jumping horizontal lines.
*/
function draw() {
  let canvas = document.getElementById('canvasBalloon') as HTMLCanvasElement;
  let ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  audioContextCreate.analyserNode!.fftSize = 2048;
  let bufferLength = audioContextCreate.analyserNode!.frequencyBinCount;
  let dataArray = new Uint8Array(bufferLength);
  audioContextCreate.analyserNode!.getByteTimeDomainData(dataArray);
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.lineWidth = 2.0;

  let gradient = ctx.createLinearGradient(canvas.width / 1.5, 0, canvas.width / 2, canvas.height);
  gradient.addColorStop(0, "lightYellow");
  gradient.addColorStop(1, "turquoise");
  ctx.fillStyle = gradient; //'turquoise';

  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = 'red'; ctx.beginPath();
  var sliceWidth = canvas.width * 1.0 / bufferLength; var x = 0;
  for (var i = 0; i < bufferLength; i++) {
    var v = dataArray[i] / 128.0;
    var y = v * canvas.height / 2;
    if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
    x += sliceWidth;
  }
  ctx.stroke();
}
;
/**
* Spectrum analyzer retro equalizer style.
*/
function animatedBars() {
  let canvas = document.getElementById('canvasBalloon') as HTMLCanvasElement;
  let ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  audioContextCreate.analyserNode!.fftSize = 128;
  const bufferLength = audioContextCreate.analyserNode!.frequencyBinCount;
  var barWidth = (canvas.width / bufferLength) * 2;
  const dataArray = new Uint8Array(bufferLength);
  audioContextCreate.analyserNode!.getByteFrequencyData(dataArray);
  let x = 0 - barWidth * 2;
  ctx.clearRect(0, 0, canvas.width, canvas.height);  // not if second anim in background

  for (let i = 0; i < bufferLength; i++) {
    let barHeight = ((dataArray[i] / 2) - 12) + 2;
    ctx.lineWidth = 3;
    ctx.fillStyle = 'red';
    ctx.fillRect(x, canvas.height - barHeight - 3, barWidth, 3);
    ctx.fillStyle = 'rgb(219, 111, 52)';
    ctx.fillRect(x, canvas.height - barHeight - 6, barWidth, 3);
    ctx.fillStyle = 'blue';
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    x += barWidth;
  }
}
;

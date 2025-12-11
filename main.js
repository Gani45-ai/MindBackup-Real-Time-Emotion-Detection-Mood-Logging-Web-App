const video = document.getElementById('video');
const status = document.getElementById('status');
const latestImg = document.getElementById('latest-img');
const latestEmoji = document.getElementById('latest-emoji');
const thumbs = document.getElementById('thumbs');
const statsDiv = document.getElementById('stats');

let capturing = true;
let lastEmotion = 'neutral';

async function startCamera(){
  try{
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    status.innerText = 'Camera active';
    setTimeout(captureLoop, 2000); // start after 2s warmup
  } catch(err){
    status.innerText = 'Camera error: ' + err.message;
  }
}

function dataURLfromVideo(){
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/png');
}

async function captureLoop(){
  if(!capturing) return;
  const imgData = dataURLfromVideo();
  try{
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({image: imgData})
    });
    const j = await res.json();
    const {emotion, confidence, emoji, filename} = j;
    updateUI(emotion, emoji, filename);
  } catch(err){
    console.error('analyze error', err);
  }
  setTimeout(captureLoop, 5000);
}

function updateUI(emotion, emoji, filename){
  lastEmotion = emotion;
  latestEmoji.innerText = emoji || '🙂';
  latestImg.src = '/memories/' + filename + '?t=' + Date.now();
  const thumb = document.createElement('div');
  thumb.className = 'thumb';
  thumb.innerHTML = `<img src="/memories/${filename}?t=${Date.now()}" /><div class="emo">${emoji}</div>`;
  thumbs.prepend(thumb);
  setMode(emotion);
  fetch('/stats').then(r=>r.json()).then(updateStats);
}

function setMode(emotion){
  const app = document.getElementById('app');
  app.className = 'mode-' + (emotion || 'neutral');
}

function updateStats(data){
  statsDiv.innerHTML = '<strong>Stats</strong><br>' +
    'Last minute: ' + JSON.stringify(data.minute) + '<br>' +
    'Today: ' + JSON.stringify(data.day);
}

startCamera();

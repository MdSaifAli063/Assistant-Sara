import json, random
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "sara_profile.json"
HOST = "127.0.0.1"
PORT = 8000

HTML_PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sara</title><style>
:root{--a:#173532;--b:#4f8b74;--c:#f7efe3;--d:#f0b7a3;--e:#d6758c}*{box-sizing:border-box}body{margin:0;font-family:"Trebuchet MS","Segoe UI",sans-serif;color:#173532;background:radial-gradient(circle at 10% 10%,#f0cf8f66,transparent 20%),radial-gradient(circle at 90% 10%,#d6758c55,transparent 18%),linear-gradient(180deg,#dcecdf,#f7efe3 50%,#f3ddd2);min-height:100vh}.wrap{width:min(1320px,calc(100% - 24px));margin:16px auto;display:grid;grid-template-columns:1.05fr 1fr;gap:18px}.panel{background:#fff9f1cc;border:1px solid #1735321a;border-radius:28px;box-shadow:0 18px 50px #12231f2b;backdrop-filter:blur(14px);overflow:hidden}.left{padding:24px}.badge{display:inline-block;padding:10px 16px;border-radius:999px;background:#fff;font-weight:800}h1{font-size:clamp(2.8rem,5vw,5rem);line-height:.92;margin:16px 0 10px}.lead{line-height:1.7;max-width:560px}.pills,.tools,.moods{display:flex;flex-wrap:wrap;gap:10px}.pill,.tool,.mood{padding:10px 14px;border-radius:999px;background:#fff;border:1px solid #17353214;box-shadow:0 10px 24px #17353214}.scene{margin-top:24px;position:relative;height:470px;border-radius:28px;overflow:hidden;background:linear-gradient(180deg,#dff1e5,#ebd5c2 60%,#c8a98e)}.sun{position:absolute;right:52px;top:32px;width:84px;height:84px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#fffce8,#efc26e 72%);box-shadow:0 0 44px #efc26eb2;animation:pulse 4s ease-in-out infinite}.speech{position:absolute;left:28px;top:64px;max-width:220px;background:#ffffffe3;padding:14px 16px;border-radius:22px 22px 22px 8px;box-shadow:0 16px 34px #1735321f;line-height:1.5}.hill{position:absolute;bottom:-70px;border-radius:50%;background:linear-gradient(180deg,#6d9f85,#2e5a4d)}.h1a{left:-40px;width:340px;height:180px}.h2a{left:180px;width:350px;height:170px;background:linear-gradient(180deg,#87ac98,#426c61)}.h3a{right:-40px;width:320px;height:180px}.avatar{position:absolute;left:50%;bottom:58px;transform:translateX(-50%);width:210px;height:350px;animation:float 5s ease-in-out infinite}.hair{position:absolute;left:50%;top:6px;transform:translateX(-50%);width:116px;height:126px;border-radius:60px 60px 50px 50px;background:linear-gradient(180deg,#49382d,#1d1511)}.head{position:absolute;left:50%;top:18px;transform:translateX(-50%);width:94px;height:108px;border-radius:48px;background:linear-gradient(180deg,#ffd9bf,#f6c5a5);z-index:2}.eye{position:absolute;top:51px;width:11px;height:11px;border-radius:50%;background:#382521;animation:blink 4.5s infinite}.l{left:25px}.r{right:25px}.smile{position:absolute;left:50%;top:74px;transform:translateX(-50%);width:28px;height:14px;border-bottom:3px solid #a06757;border-radius:0 0 18px 18px}.arm{position:absolute;top:126px;width:28px;height:110px;border-radius:18px;background:linear-gradient(180deg,#ffd9bf,#edb796)}.al{left:28px;transform:rotate(20deg)}.ar{right:28px;transform:rotate(-18deg);animation:wave 3s ease-in-out infinite}.dress{position:absolute;left:50%;top:104px;transform:translateX(-50%);width:138px;height:168px;border-radius:34px 34px 22px 22px;background:linear-gradient(180deg,#ffe7ef,#cb6f87 45%,#7a405f);box-shadow:0 16px 28px #7a405f40}.skirt{position:absolute;left:50%;top:215px;transform:translateX(-50%);width:182px;height:100px;clip-path:polygon(12% 0,88% 0,100% 100%,0 100%);background:linear-gradient(180deg,#ffd1dd,#b25a7d 55%,#68354f)}.leg{position:absolute;top:290px;width:28px;height:98px;border-radius:18px;background:linear-gradient(180deg,#ffd9bf,#eab08d)}.ll{left:72px}.lr{right:72px}.shoe{position:absolute;bottom:-4px;width:44px;height:16px;border-radius:16px;background:linear-gradient(180deg,#3c251c,#130f0d)}.ll .shoe{left:-10px}.lr .shoe{right:-10px}.right{padding:22px;display:grid;grid-template-rows:auto auto auto 1fr auto;gap:12px;min-height:900px}.top{display:flex;justify-content:space-between;gap:12px;align-items:center}.status{padding:10px 14px;border-radius:999px;background:#4f8b7420;font-weight:700}.banner{padding:16px;border-radius:24px;background:linear-gradient(135deg,#214641,#5f947e);color:#fff}.intro,.card,.chat{background:#fff9;border:1px solid #17353214;border-radius:22px}.intro,.card{padding:16px}.form{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.full{grid-column:1/-1}label{display:block;margin:0 0 6px;font-weight:700}input,textarea,button{width:100%;font:inherit}input,textarea{border:1px solid #17353218;background:#fff;border-radius:16px;padding:13px 14px}textarea{resize:vertical;min-height:84px}button{border:none;cursor:pointer;padding:13px 16px;border-radius:16px;font-weight:800}.pri{background:linear-gradient(135deg,var(--a),var(--b));color:#fff}.sec{background:#fff;border:1px solid #17353218;color:var(--a)}.main{display:grid;grid-template-columns:1fr 250px;gap:12px}.chat{padding:14px;min-height:410px;max-height:500px;overflow:auto}.bubble{max-width:min(90%,560px);padding:13px 15px;border-radius:18px;margin:0 0 12px;white-space:pre-wrap;line-height:1.55}.sara{background:#fff;border:1px solid #17353214}.user{margin-left:auto;background:#2146411a}.side{display:grid;gap:12px}.compose{display:grid;grid-template-columns:1fr auto auto;gap:10px}.hide{display:none!important}.note{text-align:center;color:#567267;font-size:.92rem}@keyframes pulse{50%{transform:scale(1.06)}}@keyframes float{50%{transform:translateX(-50%) translateY(-9px)}}@keyframes blink{0%,46%,48%,100%{transform:scaleY(1)}47%{transform:scaleY(.1)}}@keyframes wave{50%{transform:rotate(-33deg)}}@media(max-width:1050px){.wrap{grid-template-columns:1fr}.right{min-height:auto}}@media(max-width:760px){.form,.main,.compose{grid-template-columns:1fr}}</style></head><body><main class="wrap"><section class="panel left"><div class="badge">✨ Sara, your living companion</div><h1>Sara listens, speaks, and cares.</h1><div class="lead">She learns about you first, then talks like a warm friend, teaches world knowledge, asks about your health, and sends gentle check-ins through the day.</div><div class="pills"><div class="pill">🌸 friend mode</div><div class="pill">🎙️ voice</div><div class="pill">🩺 health check</div><div class="pill">🌍 world facts</div><div class="pill">💌 proactive messages</div></div><div class="scene"><div class="sun"></div><div class="speech" id="speechBubble">Hi friend, how is your health and how is today going?</div><div class="avatar"><div class="hair"></div><div class="head"><div class="eye l"></div><div class="eye r"></div><div class="smile"></div></div><div class="arm al"></div><div class="arm ar"></div><div class="dress"></div><div class="skirt"></div><div class="leg ll"><div class="shoe"></div></div><div class="leg lr"><div class="shoe"></div></div></div><div class="hill h1a"></div><div class="hill h2a"></div><div class="hill h3a"></div></div><div class="pills" style="margin-top:16px"><div class="pill">Morning: asks about body and mood</div><div class="pill">Afternoon: helps you focus</div><div class="pill">Evening: reflects gently</div></div></section><section class="panel right"><div class="top"><h2 style="margin:0">Sara Console</h2><div class="status" id="statusPill">Waiting to know you</div></div><div class="banner"><strong>Daily check-in</strong><div id="dailyPrompt" style="margin-top:8px;line-height:1.6">Sara will ask about sleep, energy, food, water, stress, and what is going on today.</div><div class="moods" style="margin-top:12px"><button class="mood sec" type="button" data-checkin="I feel energetic and clear today.">☀️ Strong</button><button class="mood sec" type="button" data-checkin="I feel okay but a little stressed and tired today.">🌿 Mixed</button><button class="mood sec" type="button" data-checkin="I feel low on energy and I want gentle support today.">🌧️ Need care</button></div></div><div class="intro" id="introBox">Tell Sara about yourself first. Then she will speak, ask about your health, and support your day more personally.</div><div id="profileSection"><form id="profileForm" class="form"><div><label for="name">Your name</label><input id="name" name="name" required placeholder="What should Sara call you?"></div><div><label for="city">City or country</label><input id="city" name="city" placeholder="Where are you from?"></div><div><label for="age">Age or life stage</label><input id="age" name="age" placeholder="Student, working professional..."></div><div><label for="mood">Current mood</label><input id="mood" name="mood" placeholder="Calm, tired, excited..."></div><div><label for="health">Health and energy</label><input id="health" name="health" placeholder="Sleep, body, energy, fitness"></div><div><label for="today">What is going on today</label><input id="today" name="today" placeholder="Class, work, errands, rest"></div><div class="full"><label for="interests">Interests</label><textarea id="interests" name="interests" placeholder="Coding, music, art, fitness, study..."></textarea></div><div class="full"><label for="goals">Goals</label><textarea id="goals" name="goals" placeholder="What do you want Sara to help you with?"></textarea></div><div class="full"><label for="routine">Routine</label><textarea id="routine" name="routine" placeholder="How your day usually goes."></textarea></div><div class="full"><button class="pri" type="submit">Save profile and wake Sara</button></div></form></div><div id="chatSection" class="hide"><div class="tools"><button class="tool sec" type="button" data-prompt="Check on my health and ask me how today is going.">🩺 Health</button><button class="tool sec" type="button" data-prompt="Teach me something interesting about the world today.">🌍 Teach</button><button class="tool sec" type="button" data-prompt="Give me one smart suggestion for today based on my goals.">🧭 Suggest</button><button class="tool sec" type="button" data-prompt="Talk to me like a caring friend.">💗 Friend</button></div><div class="main"><div id="chatLog" class="chat"></div><div class="side"><div class="card"><strong>Voice</strong><div id="voiceStatus" style="margin-top:8px;line-height:1.5;color:#4b645b">Speech ready when supported by your browser.</div></div><div class="card"><strong>Today's focus</strong><div id="focusSummary" style="margin-top:8px">Sara will summarize your day here.</div></div><div class="card"><strong>Health note</strong><div id="healthSummary" style="margin-top:8px">Sara will remind you gently about your health.</div></div></div></div><form id="chatForm" class="compose"><textarea id="message" placeholder="Message Sara..." required></textarea><button id="listenButton" class="sec" type="button">🎤 Listen</button><button class="pri" type="submit">Send</button></form></div><div class="note">Local Python backend with browser voice features.</div></section></main><script>
const profileSection=document.getElementById("profileSection"),chatSection=document.getElementById("chatSection"),profileForm=document.getElementById("profileForm"),chatForm=document.getElementById("chatForm"),chatLog=document.getElementById("chatLog"),introBox=document.getElementById("introBox"),statusPill=document.getElementById("statusPill"),messageInput=document.getElementById("message"),speechBubble=document.getElementById("speechBubble"),voiceStatus=document.getElementById("voiceStatus"),focusSummary=document.getElementById("focusSummary"),healthSummary=document.getElementById("healthSummary"),dailyPrompt=document.getElementById("dailyPrompt"),listenButton=document.getElementById("listenButton");let currentProfile=null,proactiveTimer=null;
function bubble(role,text,speak=false){const d=document.createElement("div");d.className="bubble "+role;d.textContent=text;chatLog.appendChild(d);chatLog.scrollTop=chatLog.scrollHeight;if(role==="sara"){speechBubble.textContent=text;if(speak)say(text)}}
function say(text){if(!("speechSynthesis"in window)){voiceStatus.textContent="Speech is not supported in this browser.";return}window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text.replace(/[^\w\s,.!?'-]/g," ").replace(/\s+/g," ").trim());u.rate=1;u.pitch=1.05;const v=window.speechSynthesis.getVoices();u.voice=v.find(x=>/female|zira|aria|susan|google uk english female/i.test(x.name))||v.find(x=>/english/i.test(x.lang))||v[0];u.onstart=()=>voiceStatus.textContent="Sara is speaking.";u.onend=()=>voiceStatus.textContent="Speech ready when supported by your browser.";window.speechSynthesis.speak(u)}
function setMode(p){currentProfile=p;profileSection.classList.add("hide");chatSection.classList.remove("hide");statusPill.textContent="Friend mode for "+p.name;introBox.textContent="Sara knows your profile now. She can speak, check your health, guide your day, and talk like a close friend.";focusSummary.textContent=p.today?"Today: "+p.today:"Tell Sara what is happening today.";healthSummary.textContent=p.health?"Health: "+p.health:"Tell Sara how your body and energy feel.";dailyPrompt.textContent="Sara is ready to ask about your mood, health, energy, water, food, and what is happening today for "+p.name+".";startChecks()}
function fillForm(p){Object.entries(p).forEach(([k,v])=>{const f=document.getElementById(k);if(f)f.value=v})}
async function sendMessage(message,speak=true){bubble("user",message);const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const d=await r.json();bubble("sara",d.reply,speak);if(d.focus_summary)focusSummary.textContent=d.focus_summary;if(d.health_summary)healthSummary.textContent=d.health_summary}
async function loadProfile(){const r=await fetch("/api/profile");const d=await r.json();if(!d.profile)return;fillForm(d.profile);setMode(d.profile);bubble("sara","Hi "+d.profile.name+". I am Sara. I remember you and I am ready to check on your health, ask about today, and help like a caring friend.",true)}
function startChecks(){if(proactiveTimer)clearInterval(proactiveTimer);proactiveTimer=setInterval(async()=>{if(!currentProfile||document.hidden)return;const r=await fetch("/api/checkin");const d=await r.json();if(d.message){bubble("sara",d.message,false);if(d.focus_summary)focusSummary.textContent=d.focus_summary;if(d.health_summary)healthSummary.textContent=d.health_summary}},45000)}
profileForm.addEventListener("submit",async e=>{e.preventDefault();const payload=Object.fromEntries(new FormData(profileForm).entries());const r=await fetch("/api/profile",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const d=await r.json();setMode(d.profile);chatLog.innerHTML="";bubble("sara",d.message,true)});
chatForm.addEventListener("submit",async e=>{e.preventDefault();const m=messageInput.value.trim();if(!m)return;messageInput.value="";await sendMessage(m,true)});
document.querySelectorAll("[data-prompt]").forEach(b=>b.addEventListener("click",()=>{messageInput.value=b.dataset.prompt;messageInput.focus()}));
document.querySelectorAll("[data-checkin]").forEach(b=>b.addEventListener("click",async()=>{if(!currentProfile){messageInput.value=b.dataset.checkin;messageInput.focus();return}await sendMessage(b.dataset.checkin,true)}));
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(SR){const rec=new SR();rec.lang="en-US";rec.interimResults=false;rec.maxAlternatives=1;listenButton.addEventListener("click",()=>{rec.start();voiceStatus.textContent="Listening to you now."});rec.onresult=e=>{messageInput.value=e.results[0][0].transcript;voiceStatus.textContent="Voice captured. You can send it now."};rec.onerror=()=>voiceStatus.textContent="Voice capture had a problem. You can still type.";rec.onend=()=>{if(!messageInput.value.trim())voiceStatus.textContent="Speech ready when supported by your browser."}}else{listenButton.disabled=true;voiceStatus.textContent="Voice input is not supported in this browser, but Sara can still speak on supported browsers."}
loadProfile().catch(()=>introBox.textContent="Sara could not load your profile right now, but you can fill the form and start fresh.");
</script></body></html>"""
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sara | Personal Assistant</title>
  <style>
    :root {
      --cream: #f8f2e7;
      --mist: #fffaf3;
      --forest: #27413c;
      --leaf: #5d8a6e;
      --moss: #94b49f;
      --gold: #e6b566;
      --rose: #da8d83;
      --ink: #22302b;
      --card: rgba(255, 250, 243, 0.82);
      --shadow: 0 18px 45px rgba(39, 65, 60, 0.18);
      --border: rgba(39, 65, 60, 0.12);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(230, 181, 102, 0.34), transparent 26%),
        radial-gradient(circle at top right, rgba(218, 141, 131, 0.28), transparent 23%),
        linear-gradient(180deg, #dfead9 0%, #f6ebda 55%, #f4dfd0 100%);
      overflow-x: hidden;
    }

    body::before,
    body::after {
      content: "";
      position: fixed;
      inset: auto;
      width: 320px;
      height: 320px;
      border-radius: 50%;
      filter: blur(40px);
      opacity: 0.32;
      pointer-events: none;
      z-index: 0;
    }

    body::before {
      top: -70px;
      left: -50px;
      background: #c8dfb5;
    }

    body::after {
      bottom: -90px;
      right: -40px;
      background: #f0b5a7;
    }

    .shell {
      position: relative;
      z-index: 1;
      width: min(1200px, calc(100% - 32px));
      margin: 24px auto;
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 22px;
      align-items: start;
    }

    .panel {
      background: var(--card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 28px;
      box-shadow: var(--shadow);
    }

    .hero {
      padding: 30px;
      min-height: 760px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      position: relative;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.55);
      color: var(--forest);
      padding: 8px 14px;
      border-radius: 999px;
      font-weight: 700;
      letter-spacing: 0.03em;
    }

    h1 {
      font-size: clamp(2.8rem, 5vw, 5rem);
      line-height: 0.95;
      margin: 18px 0 14px;
      color: var(--forest);
    }

    .hero p {
      font-size: 1.05rem;
      line-height: 1.7;
      max-width: 540px;
      margin: 0;
    }

    .emoji-cloud {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 22px;
    }

    .emoji-pill {
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.7);
      border: 1px solid rgba(39, 65, 60, 0.08);
      font-size: 1rem;
      box-shadow: 0 8px 24px rgba(39, 65, 60, 0.08);
      animation: drift 6s ease-in-out infinite;
    }

    .emoji-pill:nth-child(2n) {
      animation-delay: -2s;
    }

    .emoji-pill:nth-child(3n) {
      animation-delay: -4s;
    }

    @keyframes drift {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-7px) rotate(1deg); }
    }

    .story-card {
      margin-top: 26px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }

    .mini-card {
      background: rgba(255, 255, 255, 0.64);
      border-radius: 22px;
      padding: 18px;
      border: 1px solid rgba(39, 65, 60, 0.08);
      min-height: 145px;
    }

    .mini-card strong {
      display: block;
      margin-top: 10px;
      margin-bottom: 8px;
      color: var(--forest);
      font-size: 1rem;
    }

    .mini-card span {
      display: block;
      color: #42564e;
      line-height: 1.5;
      font-size: 0.95rem;
    }

    .assistant {
      padding: 24px;
      min-height: 760px;
      display: grid;
      grid-template-rows: auto auto 1fr auto;
      gap: 16px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
    }

    .topbar h2 {
      margin: 0;
      font-size: 1.5rem;
      color: var(--forest);
    }

    .status {
      padding: 10px 14px;
      border-radius: 999px;
      font-size: 0.92rem;
      background: rgba(93, 138, 110, 0.12);
      color: var(--forest);
      border: 1px solid rgba(93, 138, 110, 0.14);
    }

    .intro {
      padding: 18px;
      background: linear-gradient(135deg, rgba(230, 181, 102, 0.18), rgba(255, 255, 255, 0.7));
      border-radius: 22px;
      border: 1px solid rgba(39, 65, 60, 0.08);
      line-height: 1.6;
    }

    .profile-form {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    .profile-form .full {
      grid-column: 1 / -1;
    }

    label {
      display: block;
      font-size: 0.92rem;
      font-weight: 700;
      margin-bottom: 6px;
      color: var(--forest);
    }

    input, textarea, button {
      width: 100%;
      border: none;
      font: inherit;
    }

    input, textarea {
      padding: 14px 15px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.78);
      border: 1px solid rgba(39, 65, 60, 0.08);
      color: var(--ink);
      outline: none;
      transition: 0.2s ease;
    }

    input:focus, textarea:focus {
      border-color: rgba(39, 65, 60, 0.24);
      box-shadow: 0 0 0 4px rgba(148, 180, 159, 0.2);
    }

    textarea {
      resize: vertical;
      min-height: 92px;
    }

    button {
      cursor: pointer;
      border-radius: 18px;
      padding: 14px 18px;
      font-weight: 800;
      letter-spacing: 0.02em;
      transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
    }

    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 14px 24px rgba(39, 65, 60, 0.14);
    }

    .primary {
      background: linear-gradient(135deg, var(--forest), var(--leaf));
      color: white;
    }

    .secondary {
      background: rgba(255, 255, 255, 0.78);
      color: var(--forest);
      border: 1px solid rgba(39, 65, 60, 0.08);
    }

    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .chat {
      background: rgba(255, 255, 255, 0.48);
      border-radius: 24px;
      padding: 16px;
      overflow: auto;
      border: 1px solid rgba(39, 65, 60, 0.08);
      min-height: 280px;
      max-height: 420px;
    }

    .bubble {
      padding: 14px 16px;
      border-radius: 18px;
      margin-bottom: 12px;
      line-height: 1.55;
      width: fit-content;
      max-width: min(92%, 560px);
      white-space: pre-wrap;
      animation: fadeUp 0.35s ease;
    }

    .bubble.user {
      background: rgba(39, 65, 60, 0.12);
      margin-left: auto;
    }

    .bubble.sara {
      background: rgba(255, 255, 255, 0.84);
      border: 1px solid rgba(39, 65, 60, 0.08);
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: end;
    }

    .footer-note {
      font-size: 0.9rem;
      color: #50655c;
      text-align: center;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 980px) {
      .shell {
        grid-template-columns: 1fr;
      }

      .hero, .assistant {
        min-height: auto;
      }
    }

    @media (max-width: 640px) {
      .story-card,
      .profile-form,
      .composer {
        grid-template-columns: 1fr;
      }

      h1 {
        font-size: 2.6rem;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="panel hero">
      <div>
        <div class="badge">🌿 Storybook companion • Sara</div>
        <h1>Your warm, wise personal assistant.</h1>
        <p>
          Sara first learns about you, then talks to you like a caring friend. She can explain the world,
          offer practical suggestions, and keep your goals, interests, and daily rhythm in mind.
        </p>
        <div class="emoji-cloud">
          <div class="emoji-pill">🌤️ curious mornings</div>
          <div class="emoji-pill">🌱 gentle growth</div>
          <div class="emoji-pill">📚 tiny world lessons</div>
          <div class="emoji-pill">🍵 kind suggestions</div>
          <div class="emoji-pill">🫶 friendly check-ins</div>
          <div class="emoji-pill">✨ cozy focus</div>
        </div>
      </div>

      <div class="story-card">
        <div class="mini-card">
          <div style="font-size: 1.8rem;">🌍</div>
          <strong>Teach Me</strong>
          <span>Ask Sara about countries, science, habits, productivity, culture, and everyday knowledge.</span>
        </div>
        <div class="mini-card">
          <div style="font-size: 1.8rem;">🧭</div>
          <strong>Guide Me</strong>
          <span>Get suggestions for work, learning, routines, healthful habits, and better decisions.</span>
        </div>
        <div class="mini-card">
          <div style="font-size: 1.8rem;">🌸</div>
          <strong>Know Me</strong>
          <span>She remembers your profile and adjusts her tone, ideas, and support around your goals.</span>
        </div>
      </div>
    </section>

    <section class="panel assistant">
      <div class="topbar">
        <h2>Sara's Cottage</h2>
        <div class="status" id="statusPill">Learning about you</div>
      </div>

      <div class="intro" id="introBox">
        Tell Sara about yourself first. Once your profile is saved, she will respond like a friend, teach you
        things about the world, and give you thoughtful suggestions in daily life.
      </div>

      <div id="profileSection">
        <form id="profileForm" class="profile-form">
          <div>
            <label for="name">Your name</label>
            <input id="name" name="name" placeholder="What should Sara call you?" required>
          </div>
          <div>
            <label for="city">City or country</label>
            <input id="city" name="city" placeholder="Where are you from?">
          </div>
          <div>
            <label for="age">Age or life stage</label>
            <input id="age" name="age" placeholder="Student, working professional, etc.">
          </div>
          <div>
            <label for="mood">Current vibe</label>
            <input id="mood" name="mood" placeholder="Calm, ambitious, tired, excited...">
          </div>
          <div class="full">
            <label for="interests">Interests</label>
            <textarea id="interests" name="interests" placeholder="Books, coding, fitness, art, travel..."></textarea>
          </div>
          <div class="full">
            <label for="goals">Goals</label>
            <textarea id="goals" name="goals" placeholder="What are you trying to improve or achieve?"></textarea>
          </div>
          <div class="full">
            <label for="routine">Routine and lifestyle</label>
            <textarea id="routine" name="routine" placeholder="Your daily routine, habits, schedule, and challenges."></textarea>
          </div>
          <div class="full">
            <button class="primary" type="submit">Save profile and wake Sara</button>
          </div>
        </form>
      </div>

      <div id="chatSection" class="hidden">
        <div class="toolbar">
          <button class="secondary" type="button" data-prompt="Teach me something interesting about the world today.">🌍 Teach me</button>
          <button class="secondary" type="button" data-prompt="Give me one useful suggestion for today.">🧭 Suggest for today</button>
          <button class="secondary" type="button" data-prompt="Check in with me like a good friend.">🫶 Friendly check-in</button>
        </div>
        <div id="chatLog" class="chat"></div>
        <form id="chatForm" class="composer">
          <textarea id="message" placeholder="Talk with Sara..." required></textarea>
          <button class="primary" type="submit">Send</button>
        </form>
      </div>

      <div class="footer-note">Built as a local Python app. Your profile is stored on this computer in a small JSON file.</div>
    </section>
  </main>

  <script>
    const profileSection = document.getElementById("profileSection");
    const chatSection = document.getElementById("chatSection");
    const profileForm = document.getElementById("profileForm");
    const chatForm = document.getElementById("chatForm");
    const chatLog = document.getElementById("chatLog");
    const introBox = document.getElementById("introBox");
    const statusPill = document.getElementById("statusPill");
    const messageInput = document.getElementById("message");

    function appendBubble(role, text) {
      const bubble = document.createElement("div");
      bubble.className = "bubble " + role;
      bubble.textContent = text;
      chatLog.appendChild(bubble);
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    function setChatMode(profile) {
      profileSection.classList.add("hidden");
      chatSection.classList.remove("hidden");
      statusPill.textContent = "Friend mode for " + profile.name;
      introBox.textContent = "Sara knows your profile now. Ask for life suggestions, world lessons, habit help, or just have a warm conversation.";
    }

    async function loadProfile() {
      const response = await fetch("/api/profile");
      const data = await response.json();
      if (!data.profile) {
        return;
      }

      const profile = data.profile;
      for (const [key, value] of Object.entries(profile)) {
        const field = document.getElementById(key);
        if (field) {
          field.value = value;
        }
      }

      setChatMode(profile);
      appendBubble("sara", "Hello " + profile.name + " 🌿 I'm Sara. I know a little about you already, so we can talk like friends. Ask me to teach you something, guide your day, or simply keep you company.");
    }

    profileForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(profileForm).entries());
      const response = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      setChatMode(data.profile);
      chatLog.innerHTML = "";
      appendBubble("sara", data.message);
    });

    chatForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const message = messageInput.value.trim();
      if (!message) return;

      appendBubble("user", message);
      messageInput.value = "";

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      appendBubble("sara", data.reply);
    });

    document.querySelectorAll("[data-prompt]").forEach((button) => {
      button.addEventListener("click", () => {
        messageInput.value = button.dataset.prompt;
        messageInput.focus();
      });
    });

    loadProfile().catch((error) => {
      console.error(error);
      introBox.textContent = "Sara could not load your profile just now, but you can still fill in the form and start fresh.";
    });
  </script>
</body>
</html>
"""


def load_profile():
    if not PROFILE_PATH.exists():
        return None

    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_profile(profile):
    PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def normalize_profile(data):
    fields = ["name", "city", "age", "mood", "interests", "goals", "routine"]
    profile = {field: str(data.get(field, "")).strip() for field in fields}
    profile["name"] = profile["name"] or "friend"
    profile["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return profile


def build_welcome(profile):
    snippets = []
    if profile.get("city"):
        snippets.append(f"from {profile['city']}")
    if profile.get("interests"):
        snippets.append(f"into {profile['interests']}")
    if profile.get("goals"):
        snippets.append(f"working toward {profile['goals']}")

    detail = ", ".join(snippets) if snippets else "and ready to begin"
    return (
        f"Hi {profile['name']} 🌸 I'm Sara, your personal companion. I've learned a little about you"
        f" {detail}. From here, I'll talk with you like a friend, teach you useful things about the world,"
        " and share thoughtful suggestions whenever you need them."
    )


def world_lesson():
    lessons = [
        "🌍 Tiny world lesson: oceans regulate Earth's temperature by storing and moving heat, which is one reason coastal climates are often milder than inland ones.",
        "📚 Tiny world lesson: many of the foods we think of as everyday basics, like potatoes and tomatoes, spread globally only after long journeys across continents.",
        "🔭 Tiny world lesson: starlight is a time machine. When you look at distant stars, you're seeing light that may have started traveling years, centuries, or longer ago.",
        "🧠 Tiny world lesson: your brain learns better with spaced repetition than last-minute cramming, because review across time strengthens recall.",
    ]
    return random.choice(lessons)


def suggestion_for(profile):
    interests = profile.get("interests", "").lower()
    goals = profile.get("goals", "").lower()
    routine = profile.get("routine", "").lower()

    if "code" in interests or "program" in interests or "developer" in goals:
        return "💡 Suggestion: spend 25 focused minutes building one tiny feature, then write down exactly what you learned. Small shipping beats vague perfection."
    if "fitness" in interests or "health" in goals or "exercise" in routine:
        return "💡 Suggestion: tie movement to an existing habit. Even a 10-minute walk after meals is easier to sustain than a big plan that depends on motivation."
    if "study" in goals or "student" in profile.get("age", "").lower():
        return "💡 Suggestion: choose one topic today and teach it back in your own words. Explaining something is one of the fastest ways to see what you truly understand."

    return "💡 Suggestion: choose one important thing, one kind thing for yourself, and one small curiosity to explore today. That balance keeps life productive and human."


def friend_check_in(profile):
    mood = profile.get("mood") or "a little uncertain"
    return (
        f"🫶 Hey {profile['name']}, you don't have to do everything at once. You mentioned feeling {mood},"
        " so let's keep today gentle but meaningful. Pick one task that matters, finish it with care,"
        " and let that be enough for now."
    )


def general_response(message, profile):
    lower = message.lower()
    name = profile.get("name", "friend")

    if any(word in lower for word in ["teach", "learn", "world", "fact", "explain"]):
        return world_lesson()

    if any(word in lower for word in ["suggest", "advice", "recommend", "help me decide", "what should i do"]):
        return suggestion_for(profile)

    if any(word in lower for word in ["friend", "check in", "sad", "tired", "lonely", "stressed", "motivate"]):
        return friend_check_in(profile)

    if any(word in lower for word in ["goal", "plan", "routine", "habit", "productive"]):
        return (
            f"🌿 {name}, here's a simple way to move forward: choose a goal, break it into the next visible action,"
            " and give that action a specific time today. Progress becomes real when it has a time and shape."
        )

    if any(word in lower for word in ["hello", "hi", "hey"]):
        return f"Hello {name} 🌼 I'm here with you. Want a world lesson, a practical suggestion, or just a friendly conversation?"

    return (
        f"✨ {name}, I hear you. Based on what you've shared about your interests and goals, I'd suggest keeping things clear and kind:"
        f" {suggestion_for(profile)}\n\n{world_lesson()}"
    )


class SaraHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, payload, status=HTTPStatus.OK):
        body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length) if length else b"{}"
        return json.loads(data.decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(HTML_PAGE)
            return
        if path == "/api/profile":
            self._send_json({"profile": load_profile()})
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/profile":
            payload = self._read_json()
            profile = normalize_profile(payload)
            save_profile(profile)
            self._send_json({"profile": profile, "message": build_welcome(profile)})
            return

        if path == "/api/chat":
            profile = load_profile()
            if not profile:
                self._send_json(
                    {"reply": "Please tell me about yourself first so I can speak with you more personally."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            payload = self._read_json()
            message = str(payload.get("message", "")).strip()
            if not message:
                self._send_json({"reply": "I'm listening. Tell me what's on your mind."})
                return

            self._send_json({"reply": general_response(message, profile)})
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format, *args):
        return


def run():
    server = ThreadingHTTPServer((HOST, PORT), SaraHandler)
    print(f"Sara is ready at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSara is going to rest. Bye.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()

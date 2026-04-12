import json
import random
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR   = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "sara_profile.json"
HOST = "127.0.0.1"
PORT = 8010

# ─────────────────────────────────────────────────────────────────────────────
# HTML / CSS / JS  (everything embedded in one file for easy deployment)
# ─────────────────────────────────────────────────────────────────────────────
HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sara — Your Room Companion</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Nunito:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
/* ════════════════════════════════════════════════════════════
   DESIGN TOKENS
════════════════════════════════════════════════════════════ */
:root{
  /* Room palette — airy peach studio */
  --wall-a:#fff4ea; --wall-b:#f8e7d7; --wall-c:#efd7c6;
  --floor-a:#d9b184; --floor-b:#ba8a5f; --floor-c:#936748;
  --sky-a:#88d8ff;  --sky-b:#cdefff;  --sky-c:#f6fdff;
  --grass-a:#74c67a;--grass-b:#4e9f59;
  /* Accent palette */
  --coral:#ef7c6d;  --teal:#52b8b0;   --violet:#7e74d8;
  --gold:#ecb45b;   --rose:#ef7d9d;   --mint:#69c9a2;
  --amber:#e89a4a; --sky:#4c9ad9;
  /* UI */
  --panel-bg:#fffaf6; --panel-2:#fff1e8;
  --text-light:#35263d; --text-mute:#8d778d;
  --card-bg:rgba(255,255,255,.72); --card-border:rgba(210,170,190,.28);
  --accent:#e77aa0; --accent2:#6db8c8;
  --r:18px;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{
  font-family:'Nunito',sans-serif;
  background:
    radial-gradient(circle at top left,rgba(255,214,224,.75),transparent 30%),
    linear-gradient(135deg,#fffaf7 0%,#fff3ee 48%,#f7efe9 100%);
  color:var(--text-light);
}

/* ════════════════════════════════════════════════════════════
   APP SHELL
════════════════════════════════════════════════════════════ */
.app{display:grid;grid-template-columns:1fr 420px;height:100vh}

/* ════════════════════════════════════════════════════════════
   ROOM CONTAINER
════════════════════════════════════════════════════════════ */
.room-wrap{
  position:relative;overflow:hidden;
  background:
    radial-gradient(circle at 20% 18%,rgba(255,226,214,.9),transparent 22%),
    linear-gradient(160deg,#fff6f0 0%,#fde8e1 52%,#f8ddd3 100%);
}

/* ─── 3-D ROOM BOX ─── */
.scene{position:absolute;inset:0;perspective:800px;perspective-origin:50% 40%}
.room-box{position:absolute;inset:0;transform-style:preserve-3d}

/* Back wall */
.wall-back{
  position:absolute;inset:0 0 32% 0;
  background:
    linear-gradient(180deg,var(--wall-a) 0%,var(--wall-b) 60%,var(--wall-c) 100%);
}
/* decorative wallpaper dots */
.wall-back::before{
  content:'';position:absolute;inset:0;
  background-image:
    radial-gradient(circle,rgba(200,140,80,.18) 1.5px,transparent 1.5px);
  background-size:44px 44px;
  background-position:22px 22px;
}
/* wainscoting panel lower 30% */
.wall-back::after{
  content:'';position:absolute;left:0;right:0;bottom:0;height:30%;
  background:linear-gradient(180deg,#e0c898,#cdb070);
  border-top:4px solid rgba(180,130,60,.45);
  box-shadow:inset 0 8px 20px rgba(0,0,0,.08);
}

/* Side walls — perspective wedges */
.wall-left{
  position:absolute;top:0;bottom:32%;left:0;width:20%;
  background:linear-gradient(90deg,#d4bc90,#e8d4a8);
  transform-origin:left center;
  transform:rotateY(55deg);
}
.wall-right{
  position:absolute;top:0;bottom:32%;right:0;width:20%;
  background:linear-gradient(270deg,#d4bc90,#e8d4a8);
  transform-origin:right center;
  transform:rotateY(-55deg);
}

/* Ceiling strip */
.ceiling{
  position:absolute;top:0;left:0;right:0;height:6px;
  background:linear-gradient(180deg,#c8a870,#e0c898);
  z-index:1;
}

/* Floor */
.floor{
  position:absolute;left:0;right:0;bottom:0;height:34%;
  background:linear-gradient(180deg,var(--floor-a),var(--floor-b),var(--floor-c));
  transform-origin:bottom;
  transform:rotateX(38deg) translateY(8px);
  overflow:hidden;
}
/* wood grain planks */
.floor::before{
  content:'';position:absolute;inset:0;
  background:repeating-linear-gradient(
    90deg,transparent 0px,transparent 89px,
    rgba(0,0,0,.07) 89px,rgba(0,0,0,.07) 90px
  );
}
.floor::after{
  content:'';position:absolute;inset:0;
  background:repeating-linear-gradient(
    0deg,transparent 0px,transparent 19px,
    rgba(255,255,255,.04) 19px,rgba(255,255,255,.04) 20px
  );
}

/* ─── WINDOW ─── */
.window-outer{
  position:absolute;top:5%;left:50%;transform:translateX(-50%);
  width:30%;z-index:3;
}
.window-frame{
  background:#fff8f0;
  border:16px solid #c8905a;
  border-radius:10px 10px 4px 4px;
  overflow:hidden;
  aspect-ratio:3/4;
  box-shadow:
    0 0 0 4px #a87040,
    8px 12px 40px rgba(0,0,0,.25),
    inset 0 0 0 2px rgba(255,255,255,.5);
  position:relative;
}
/* sky gradient */
.win-sky{
  position:absolute;inset:0;
  background:linear-gradient(180deg,#4fa8e0 0%,#87ceeb 45%,#b8e8ff 70%,#dff5a0 100%);
  overflow:hidden;
}
/* animated sun */
.sun{
  position:absolute;right:16%;top:12%;
  width:38px;height:38px;
  background:radial-gradient(circle at 35% 35%,#fff8c0,#ffd020 60%,#ffaa00);
  border-radius:50%;
  box-shadow:0 0 24px 8px rgba(255,200,0,.5);
  animation:sunPulse 4s ease-in-out infinite;
}
@keyframes sunPulse{50%{box-shadow:0 0 36px 14px rgba(255,200,0,.4)}}
/* clouds */
.cloud{position:absolute;animation:cloudDrift linear infinite}
.cloud-body{background:#fff;border-radius:50px;position:relative}
.cloud-b1{position:absolute;background:#fff;border-radius:50%}
.c1 .cloud-body{width:64px;height:20px;top:22%;left:-70px}
.c1 .cloud-b1{width:36px;height:30px;top:-16px;left:8px}
.c1{animation-duration:20s;animation-delay:0s}
.c2 .cloud-body{width:48px;height:16px;top:40%;left:-55px;opacity:.9}
.c2 .cloud-b1{width:26px;height:22px;top:-13px;left:6px}
.c2{animation-duration:27s;animation-delay:7s}
.c3 .cloud-body{width:56px;height:18px;top:58%;left:-65px;opacity:.75}
.c3 .cloud-b1{width:30px;height:26px;top:-14px;left:8px}
.c3{animation-duration:23s;animation-delay:3s}
@keyframes cloudDrift{to{transform:translateX(600px)}}
/* hills */
.hill{position:absolute;bottom:0;border-radius:60% 60% 0 0}
.h1{width:130%;height:44%;left:-15%;background:linear-gradient(180deg,#6abb70,#4a9a50)}
.h2{width:90%;height:34%;left:5%;background:linear-gradient(180deg,#58a860,#3a8840)}
.h3{width:70%;height:26%;right:-5%;background:linear-gradient(180deg,#7acc80,#5aac60)}
/* tiny trees */
.win-tree{position:absolute;bottom:24%}
.win-tree-trunk{width:5px;height:16px;background:#6a3e20;margin:0 auto;border-radius:1px}
.win-tree-top{width:0;border-left:10px solid transparent;border-right:10px solid transparent;border-bottom:22px solid #2e7a38;margin:0 auto;margin-top:-3px}
/* cross bars */
.win-h{position:absolute;top:50%;left:0;right:0;height:5px;background:#c8905a;transform:translateY(-50%);z-index:2}
.win-v{position:absolute;left:50%;top:0;bottom:0;width:5px;background:#c8905a;transform:translateX(-50%);z-index:2}
/* curtains */
.curtain-wrap{position:absolute;inset:-16px;z-index:4;pointer-events:none}
.curtain-l,.curtain-r{
  position:absolute;top:0;bottom:0;width:36%;
  background:linear-gradient(180deg,#e84070,#ff6898,#c82858);
  box-shadow:inset -4px 0 12px rgba(0,0,0,.15);
}
.curtain-l{
  left:0;
  clip-path:polygon(0 0,100% 0,75% 100%,0 100%);
}
.curtain-r{
  right:0;
  clip-path:polygon(0 0,100% 0,100% 100%,25% 100%);
}
.curtain-l::before,.curtain-r::before{
  content:'';position:absolute;
  top:0;width:100%;height:100%;
  background:repeating-linear-gradient(
    180deg,
    transparent 0,transparent 18px,
    rgba(255,255,255,.08) 18px,rgba(255,255,255,.08) 20px
  );
}
.valance{
  position:absolute;top:-16px;left:-16px;right:-16px;height:26px;
  background:linear-gradient(90deg,#c02050,#f04880,#e83068,#f04880,#c02050);
  border-radius:4px;z-index:5;
  box-shadow:0 4px 12px rgba(0,0,0,.2);
}
/* window sill */
.win-sill{
  height:14px;background:linear-gradient(180deg,#d4a06a,#b07838);
  border-radius:0 0 6px 6px;
  box-shadow:0 4px 10px rgba(0,0,0,.2);
}
/* window flower box */
.flower-box{
  height:18px;background:linear-gradient(180deg,#c84830,#a03020);
  border-radius:4px;
  position:relative;overflow:visible;
}
.flower{position:absolute;bottom:10px;font-size:18px}
.f1{left:8px}.f2{left:28px}.f3{left:50px}.f4{right:8px}.f5{right:28px}

/* ─── WALL DECOR ─── */
/* Hanging picture frame */
.picture-frame{
  position:absolute;left:7%;top:14%;
  width:12%;aspect-ratio:1;
  background:linear-gradient(135deg,#60a8d0,#9050c0,#e05080);
  border:6px solid #c8a060;
  border-radius:4px;
  box-shadow:4px 6px 20px rgba(0,0,0,.2),inset 0 0 0 2px rgba(255,255,255,.2);
  z-index:2;
}
.picture-frame::before{/* nail */
  content:'';position:absolute;top:-14px;left:50%;transform:translateX(-50%);
  width:4px;height:10px;background:#a07838;border-radius:2px;
}
.picture-frame::after{/* abstract art lines */
  content:'';position:absolute;inset:4px;
  background:radial-gradient(circle at 30% 30%,rgba(255,255,255,.3),transparent 60%),
             radial-gradient(circle at 70% 70%,rgba(255,255,255,.2),transparent 50%);
}
/* Clock on wall */
.wall-clock{
  position:absolute;right:26%;top:10%;
  width:52px;height:52px;
  background:#fff8e8;
  border:4px solid #c8a060;
  border-radius:50%;
  box-shadow:2px 4px 14px rgba(0,0,0,.18);
  z-index:2;
  display:flex;align-items:center;justify-content:center;
  font-size:.55rem;font-weight:800;color:#5a3820;
}

/* ─── BOOKSHELF ─── */
.bookshelf{
  position:absolute;right:4%;top:5%;
  width:17%;z-index:3;
}
.shelf-unit{
  background:linear-gradient(180deg,#7a4828,#5a3018);
  border-radius:10px 10px 4px 4px;
  padding:6px;
  box-shadow:6px 10px 30px rgba(0,0,0,.35),inset -3px 0 8px rgba(0,0,0,.2);
}
.shelf-row{
  background:linear-gradient(180deg,#9a6038,#7a4020);
  border-radius:4px;
  padding:5px 3px 6px;
  margin-bottom:5px;
  display:flex;align-items:flex-end;gap:2px;
  position:relative;
}
.shelf-row::after{
  content:'';position:absolute;left:0;right:0;bottom:0;height:5px;
  background:rgba(0,0,0,.25);border-radius:0 0 4px 4px;
}
.shelf-row:last-child{margin-bottom:0}
.bk{border-radius:2px 2px 0 0;flex-shrink:0}
/* Row 1 */
.b01{width:11px;height:40px;background:linear-gradient(180deg,#e84040,#b82020)}
.b02{width:9px;height:50px;background:linear-gradient(180deg,#f0a020,#c07800)}
.b03{width:13px;height:36px;background:linear-gradient(180deg,#4090e0,#1860b0)}
.b04{width:8px;height:46px;background:linear-gradient(180deg,#50c070,#208840)}
.b05{width:12px;height:38px;background:linear-gradient(180deg,#d060c0,#a03090)}
.b06{width:10px;height:44px;background:linear-gradient(180deg,#60d0d0,#1898a0)}
/* Row 2 */
.b07{width:14px;height:42px;background:linear-gradient(180deg,#f08050,#c04820)}
.b08{width:9px;height:52px;background:linear-gradient(180deg,#8060e0,#5030a0)}
.b09{width:11px;height:38px;background:linear-gradient(180deg,#50b880,#287850)}
.b10{width:13px;height:48px;background:linear-gradient(180deg,#e8c040,#b08800)}
.b11{width:10px;height:34px;background:linear-gradient(180deg,#e05070,#a82848)}
.mini-globe{width:18px;height:18px;background:radial-gradient(circle at 35% 30%,#60c0ff,#0060b0);border-radius:50%;margin-bottom:2px;box-shadow:0 2px 6px rgba(0,0,0,.3)}
/* Row 3 */
.b12{width:12px;height:44px;background:linear-gradient(180deg,#a0e060,#609030)}
.b13{width:10px;height:36px;background:linear-gradient(180deg,#ff8080,#e03030)}
.b14{width:14px;height:54px;background:linear-gradient(180deg,#60a8f0,#2060c0)}
.b15{width:9px;height:40px;background:linear-gradient(180deg,#f0c080,#c08830)}
.shelf-plant-sm{width:16px;height:20px;background:linear-gradient(180deg,#50a060,#307040);border-radius:50% 50% 3px 3px;margin-bottom:2px}

/* ─── RUG ─── */
.rug{
  position:absolute;left:50%;bottom:33%;
  transform:translateX(-50%) rotateX(40deg);
  width:52%;height:70px;
  background:
    linear-gradient(90deg,#8020a0 0%,#c040e0 20%,#e060ff 50%,#c040e0 80%,#8020a0 100%);
  border-radius:10px;z-index:3;
  box-shadow:0 10px 24px rgba(0,0,0,.25);
}
.rug::before{
  content:'';position:absolute;inset:6px;
  border:3px solid rgba(255,255,255,.25);border-radius:6px;
}
.rug::after{
  content:'';position:absolute;inset:12px;
  background:repeating-linear-gradient(
    90deg,transparent 0,transparent 10px,
    rgba(255,255,255,.1) 10px,rgba(255,255,255,.1) 12px
  );
}

/* ─── DESK ─── */
.desk-wrap{
  position:absolute;left:50%;bottom:32%;
  transform:translateX(-50%);
  width:60%;z-index:5;
}
.desk-top{
  background:linear-gradient(180deg,#b87848,#8a5828);
  border-radius:12px 12px 0 0;height:16px;
  box-shadow:-2px -4px 12px rgba(255,255,255,.08),0 4px 8px rgba(0,0,0,.2);
  position:relative;
}
.desk-top::before{/* desk edge highlight */
  content:'';position:absolute;top:2px;left:16px;right:16px;height:3px;
  background:rgba(255,255,255,.2);border-radius:2px;
}
.desk-body{
  background:linear-gradient(180deg,#8a5828,#6a3c10);
  height:12px;
}
.desk-legs{display:flex;justify-content:space-between;padding:0 12px}
.desk-leg{
  width:10px;height:52px;
  background:linear-gradient(180deg,#6a3c10,#4a2408);
  border-radius:0 0 5px 5px;
}
/* items on desk */
.desk-items{
  position:absolute;bottom:16px;left:0;right:0;
  display:flex;align-items:flex-end;gap:6px;padding:0 8px;
}
/* Laptop */
.laptop{position:relative;margin-left:12px}
.laptop-screen{
  width:70px;height:46px;
  background:linear-gradient(160deg,#0a1a30,#0d2040);
  border:3px solid #4a6080;border-radius:5px 5px 0 0;
  overflow:hidden;position:relative;
}
.laptop-screen::before{/* screen content */
  content:'';position:absolute;inset:4px;
  background:linear-gradient(135deg,#0a3060,#0060a0 40%,#00a0c0);
  border-radius:2px;
}
.laptop-screen::after{/* code lines */
  content:'';position:absolute;left:6px;top:7px;right:6px;
  height:2px;background:rgba(0,255,180,.4);
  box-shadow:0 5px 0 rgba(0,200,255,.3),0 10px 0 rgba(100,255,200,.2),0 15px 0 rgba(0,255,180,.15),0 20px 0 rgba(0,200,255,.1);
}
.laptop-hinge{width:74px;height:4px;background:linear-gradient(180deg,#6080a0,#405060);border-radius:0 0 3px 3px}
.laptop-base{width:78px;height:6px;background:linear-gradient(180deg,#a0b8c8,#7090a8);border-radius:0 0 4px 4px}
/* Mug */
.mug-wrap{position:relative;margin-left:4px}
.mug{
  width:26px;height:30px;
  background:linear-gradient(160deg,#fff0e0,#e8d8c0);
  border-radius:4px 4px 8px 8px;
  position:relative;overflow:hidden;
}
.mug-liquid{
  position:absolute;top:7px;left:3px;right:3px;height:8px;
  background:linear-gradient(180deg,#d0783a,#b05a18);
  border-radius:2px;
}
.mug-handle{
  position:absolute;right:-9px;top:7px;
  width:9px;height:14px;
  border:3px solid #e8d8c0;border-left:none;
  border-radius:0 7px 7px 0;
}
.steam{position:absolute;bottom:30px;left:4px;display:flex;gap:5px}
.steam-p{
  width:3px;border-radius:2px;
  background:linear-gradient(0deg,transparent,rgba(255,255,255,.7));
  animation:steamUp 2.2s ease-in-out infinite;
}
.steam-p:nth-child(1){height:14px;animation-delay:0s}
.steam-p:nth-child(2){height:18px;animation-delay:.5s}
.steam-p:nth-child(3){height:12px;animation-delay:1s}
@keyframes steamUp{
  0%,100%{opacity:0;transform:translateY(0) scaleX(1)}
  45%{opacity:1;transform:translateY(-10px) scaleX(1.8)}
  80%{opacity:0;transform:translateY(-20px) scaleX(.4)}
}
/* Desk lamp */
.lamp{position:absolute;left:6px;bottom:16px;z-index:6}
.lamp-base{width:22px;height:7px;background:linear-gradient(180deg,#c0c8d8,#8090a8);border-radius:12px}
.lamp-pole{
  width:5px;height:34px;
  background:linear-gradient(180deg,#c0c8d8,#8090a8);
  margin:0 auto;border-radius:3px;
  transform:rotate(-8deg);transform-origin:bottom center;
}
.lamp-arm{
  width:5px;height:24px;
  background:linear-gradient(180deg,#c0c8d8,#8090a8);
  margin:0 auto;border-radius:3px;
  transform:rotate(22deg);transform-origin:bottom left;margin-left:4px;
}
.lamp-shade{
  width:36px;height:18px;
  background:linear-gradient(180deg,#f8d040,#e0a000);
  border-radius:50% 50% 10px 10px;
  margin-left:-10px;
  box-shadow:0 12px 30px rgba(240,180,0,.5);
  position:relative;
}
.lamp-glow{
  position:absolute;top:16px;left:-14px;
  width:64px;height:24px;
  background:radial-gradient(ellipse,rgba(240,180,0,.3),transparent 70%);
  border-radius:50%;pointer-events:none;
}
/* Desk plant */
.deskplant{position:relative;margin-left:auto;margin-right:8px}
.dpot{width:26px;height:20px;background:linear-gradient(180deg,#d84028,#a02810);border-radius:2px 2px 7px 7px;clip-path:polygon(5% 0,95% 0,100% 100%,0 100%)}
.dstem{width:3px;height:30px;background:linear-gradient(180deg,#48a058,#288038);margin:0 auto;margin-top:-2px;border-radius:2px}
.dl{position:absolute;background:linear-gradient(135deg,#60c070,#30a040);border-radius:50%}
.dl1{width:22px;height:13px;top:2px;left:-15px;transform:rotate(-28deg)}
.dl2{width:20px;height:12px;top:7px;right:-13px;transform:rotate(24deg)}
.dl3{width:18px;height:11px;top:14px;left:-11px;transform:rotate(-44deg)}
.dl4{width:15px;height:10px;top:-2px;left:3px;transform:rotate(12deg)}
/* Notebook on desk */
.notebook{
  width:38px;height:48px;
  background:linear-gradient(180deg,#ff9060,#e06030);
  border-radius:3px 6px 6px 3px;
  margin-bottom:0;margin-left:4px;
  position:relative;overflow:hidden;
}
.notebook::before{/* lines */
  content:'';position:absolute;inset:6px 4px;
  background:repeating-linear-gradient(180deg,transparent,transparent 5px,rgba(255,255,255,.4) 5px,rgba(255,255,255,.4) 6px);
}
.notebook::after{/* spine */
  content:'';position:absolute;left:0;top:0;bottom:0;width:6px;
  background:linear-gradient(180deg,#c04010,#e06030);
}

/* ─── FAIRY LIGHTS (string on wall) ─── */
.lights-string{
  position:absolute;top:3%;left:3%;right:3%;
  height:30px;z-index:2;pointer-events:none;
}
.lights-string svg{width:100%;height:100%;overflow:visible}
.fairy-light{animation:glow 1.8s ease-in-out infinite}
.fl1{animation-delay:0s} .fl2{animation-delay:.25s} .fl3{animation-delay:.5s}
.fl4{animation-delay:.75s} .fl5{animation-delay:1s} .fl6{animation-delay:1.25s}
.fl7{animation-delay:1.5s} .fl8{animation-delay:.1s} .fl9{animation-delay:.6s}
.fl10{animation-delay:1.1s}
@keyframes glow{
  0%,100%{opacity:.6;filter:blur(0px)}
  50%{opacity:1;filter:blur(1.5px)}
}

/* ─── SARA AVATAR ─── */
.avatar-wrap{
  position:absolute;left:50%;bottom:24%;
  transform:translateX(-50%) scale(1.28);
  z-index:10;
  animation:saraFloat 5s ease-in-out infinite;
  filter:drop-shadow(0 28px 56px rgba(255,150,180,.32));
}
@keyframes saraFloat{
  0%,100%{transform:translateX(-50%) scale(1.28) translateY(0px)}
  50%{transform:translateX(-50%) scale(1.28) translateY(-14px)}
}
.avatar-shadow{
  position:absolute;bottom:-8px;left:50%;
  transform:translateX(-50%);
  width:120px;height:22px;
  background:radial-gradient(ellipse,rgba(100,100,150,.35),transparent 70%);
  border-radius:50%;
  filter:blur(2px);
}
.sara-svg{width:198px;filter:drop-shadow(0 24px 42px rgba(227,125,157,.28));}

/* ─── SPEECH BUBBLE ─── */
.speech{
  position:absolute;
  left:calc(50% + 120px);
  bottom:calc(33% + 220px);
  max-width:200px;
  background:rgba(255,255,255,.92);
  border:1.5px solid rgba(255,150,180,.45);
  border-radius:20px 20px 20px 4px;
  padding:13px 15px;
  font-size:.78rem;line-height:1.65;
  color:#5c3e54;
  box-shadow:0 20px 50px rgba(227,125,157,.2);
  z-index:11;
  animation:popIn .5s cubic-bezier(.34,1.56,.64,1);
  backdrop-filter:blur(10px);
}
.speech::before{/* triangle tail */
  content:'';position:absolute;
  bottom:-1px;left:-10px;
  border:8px solid transparent;
  border-right-color:rgba(233,173,193,.55);
  border-bottom-color:rgba(233,173,193,.55);
}
@keyframes popIn{from{opacity:0;transform:scale(.7) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}

/* ─── ROOM OVERLAYS ─── */
.room-vignette{
  position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 40%,transparent 36%,rgba(150,103,109,.12) 100%);
  pointer-events:none;z-index:20;
}
.room-border{
  position:absolute;inset:0;
  border:20px solid rgba(255,250,245,.62);
  pointer-events:none;z-index:21;
  box-shadow:inset 0 0 80px rgba(177,126,123,.16);
}

/* ─── ROOM HEADER ─── */
.room-hdr{
  position:absolute;top:16px;left:16px;right:16px;
  display:flex;justify-content:space-between;align-items:center;
  z-index:22;
}
.rbadge{
  background:rgba(255,255,255,.68);
  color:#7b5b71;
  padding:8px 16px;border-radius:999px;
  font-size:.75rem;font-weight:700;letter-spacing:.06em;
  backdrop-filter:blur(16px);
  border:1px solid rgba(224,170,191,.42);
}
.rclock{
  background:rgba(255,255,255,.68);
  color:#7b5b71;
  padding:8px 18px;border-radius:999px;
  font:.75rem/1 'Playfair Display',serif;
  backdrop-filter:blur(16px);
  border:1px solid rgba(224,170,191,.42);
}

/* ════════════════════════════════════════════════════════════
   RIGHT PANEL
════════════════════════════════════════════════════════════ */
.panel{
  display:flex;flex-direction:column;
  background:var(--panel-bg);
  border-left:1px solid rgba(230,188,202,.42);
  overflow:hidden;
  position:relative;
}
/* subtle gradient shimmer background */
.panel::before{
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse at 80% 10%,rgba(231,122,160,.12),transparent 60%),
    radial-gradient(ellipse at 20% 90%,rgba(109,184,200,.12),transparent 60%);
  pointer-events:none;
}

/* Panel header */
.p-head{
  padding:18px 20px 14px;
  border-bottom:1px solid rgba(230,188,202,.42);
  position:relative;z-index:1;
}
.p-title{
  font-family:'Playfair Display',serif;
  font-size:1.6rem;
  background:linear-gradient(135deg,#d76d95,#f2a177);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  line-height:1;
}
.p-sub{font-size:.75rem;color:var(--text-mute);margin-top:5px;font-weight:600}

/* Status pills */
.p-pills{
  display:flex;gap:6px;padding:10px 20px;flex-wrap:wrap;
  border-bottom:1px solid rgba(160,100,255,.08);
  position:relative;z-index:1;
}
.spill{
  padding:5px 12px;border-radius:999px;
  font-size:.7rem;font-weight:700;letter-spacing:.04em;
  border:1px solid rgba(255,255,255,.1);
}
.sp-a{background:rgba(80,200,120,.12);color:#70e898;border-color:rgba(80,200,120,.25)}
.sp-b{background:rgba(255,100,160,.1);color:#ff90c0;border-color:rgba(255,100,160,.2)}
.sp-c{background:rgba(160,100,255,.1);color:#c090ff;border-color:rgba(160,100,255,.2)}

/* Check-in banner */
.ci-banner{
  margin:12px 20px 0;
  background:linear-gradient(135deg,rgba(255,236,228,.95),rgba(255,245,240,.96));
  border:1px solid rgba(230,188,202,.5);
  border-radius:16px;padding:14px 16px;
  position:relative;z-index:1;
  box-shadow:0 14px 28px rgba(213,151,158,.12);
}
.ci-banner strong{font-size:.82rem;color:#b56485;letter-spacing:.03em}
.ci-text{font-size:.76rem;margin-top:4px;color:#8b6e82;line-height:1.55}
.mood-row{display:flex;gap:7px;margin-top:10px;flex-wrap:wrap}
.mood-btn{
  padding:6px 13px;border-radius:999px;
  border:1px solid rgba(230,188,202,.6);
  background:rgba(255,255,255,.7);
  color:#9c647f;
  font:700 .72rem 'Nunito',sans-serif;
  cursor:pointer;transition:all .2s;
  box-shadow:0 8px 18px rgba(222,166,181,.12);
}
.mood-btn:hover{background:#fff;border-color:#d889aa}

/* ─── LANG TOGGLE ─── */
.lang-row{
  display:flex;gap:8px;padding:10px 20px;
  border-bottom:1px solid rgba(230,188,202,.32);
  position:relative;z-index:1;align-items:center;
}
.lang-label{font-size:.72rem;color:var(--text-mute);font-weight:700;letter-spacing:.04em;margin-right:4px}
.lang-btn{
  padding:5px 14px;border-radius:999px;
  font:700 .72rem 'Nunito',sans-serif;
  cursor:pointer;transition:all .2s;border:1px solid;
}
.lang-btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
.lang-btn:not(.active){background:rgba(255,255,255,.66);border-color:rgba(230,188,202,.5);color:var(--text-mute)}
.voice-indicator{
  margin-left:auto;display:flex;align-items:center;gap:6px;
  font-size:.72rem;color:var(--text-mute);
}
.voice-dot{
  width:8px;height:8px;border-radius:50%;background:#444;
  transition:background .3s;
}
.voice-dot.speaking{background:#50e090;animation:voicePulse .6s ease-in-out infinite alternate}
.voice-dot.listening{background:#ff9040;animation:voicePulse .4s ease-in-out infinite alternate}
@keyframes voicePulse{to{transform:scale(1.5);opacity:.6}}

/* Scrollable content */
.content-area{
  flex:1;overflow-y:auto;padding:12px 20px 0;
  position:relative;z-index:1;
}
.content-area::-webkit-scrollbar{width:3px}
.content-area::-webkit-scrollbar-track{background:transparent}
.content-area::-webkit-scrollbar-thumb{background:rgba(160,100,255,.25);border-radius:2px}

/* Profile form */
.intro-card{
  font-size:.8rem;color:#8b6e82;line-height:1.65;
  margin-bottom:14px;
  padding:12px 14px;
  background:var(--card-bg);
  border:1px solid var(--card-border);
  border-radius:12px;
}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.fg-full{grid-column:1/-1}
.flabel{display:block;font-size:.7rem;font-weight:800;color:#a96d88;letter-spacing:.05em;margin-bottom:5px}
.finput,.ftextarea{
  width:100%;
  font:400 .8rem 'Nunito',sans-serif;
  background:rgba(255,255,255,.8);
  border:1.5px solid rgba(230,188,202,.5);
  border-radius:10px;padding:10px 12px;
  color:var(--text-light);transition:border-color .2s,background .2s;outline:none;
}
.finput::placeholder,.ftextarea::placeholder{color:rgba(144,120,138,.55)}
.finput:focus,.ftextarea:focus{border-color:var(--accent);background:#fff}
.ftextarea{resize:vertical;min-height:64px}
.btn-save{
  width:100%;padding:13px;
  background:linear-gradient(135deg,#e77aa0,#f0a37c,#7ac6c7);
  color:#fff;border:none;border-radius:12px;
  font:800 .88rem 'Nunito',sans-serif;
  cursor:pointer;margin-top:4px;
  transition:opacity .2s,transform .1s;
  letter-spacing:.03em;
  box-shadow:0 12px 24px rgba(228,140,148,.24);
}
.btn-save:hover{opacity:.9}
.btn-save:active{transform:scale(.97)}

/* Chat */
.chat-log{display:flex;flex-direction:column;gap:10px;padding-bottom:12px}
.bbl{
  max-width:87%;padding:11px 14px;
  border-radius:14px;font-size:.8rem;line-height:1.65;white-space:pre-wrap;
}
.bbl-sara{
  background:var(--card-bg);border:1px solid var(--card-border);
  border-radius:4px 14px 14px 14px;align-self:flex-start;
  color:var(--text-light);
}
.bbl-user{
  background:linear-gradient(135deg,#e77aa0,#f0a37c);
  color:#fff;border-radius:14px 4px 14px 14px;align-self:flex-end;
}

/* Side info cards */
.side-cards{display:grid;gap:8px;padding-bottom:12px}
.scard{
  background:var(--card-bg);border:1px solid var(--card-border);
  border-radius:12px;padding:11px 13px;
}
.scard-title{font-size:.67rem;font-weight:800;color:#a96d88;letter-spacing:.06em;text-transform:uppercase;margin-bottom:5px}
.scard-body{font-size:.77rem;color:var(--text-mute);line-height:1.5}

/* Tool row */
.tool-row{
  display:flex;gap:7px;flex-wrap:wrap;
  padding:10px 20px;
  border-top:1px solid rgba(230,188,202,.32);
  position:relative;z-index:1;
}
.tool-btn{
  padding:6px 13px;border-radius:999px;
  border:1px solid rgba(230,188,202,.5);
  background:rgba(255,255,255,.7);
  color:#a96d88;
  font:700 .72rem 'Nunito',sans-serif;
  cursor:pointer;transition:all .2s;
}
.tool-btn:hover{background:var(--accent);border-color:var(--accent);color:#fff}

/* Compose bar */
.compose{
  padding:10px 20px 14px;
  border-top:1px solid rgba(230,188,202,.35);
  background:rgba(255,250,247,.9);
  display:grid;grid-template-columns:1fr auto auto auto;
  gap:8px;align-items:end;
  position:relative;z-index:1;
}
.c-input{
  font:400 .82rem 'Nunito',sans-serif;
  background:#fff;
  border:1.5px solid rgba(230,188,202,.5);
  border-radius:12px;padding:10px 14px;
  resize:none;min-height:42px;max-height:110px;
  outline:none;color:var(--text-light);
  transition:border-color .2s;
  box-shadow:0 12px 24px rgba(227,176,186,.1);
}
.c-input::placeholder{color:rgba(144,120,138,.55)}
.c-input:focus{border-color:var(--accent)}
.c-btn{
  width:42px;height:42px;border-radius:11px;
  display:grid;place-items:center;font-size:1rem;
  cursor:pointer;transition:all .2s;border:none;
}
.c-btn-ghost{background:rgba(255,255,255,.92);color:#a96d88;border:1.5px solid rgba(230,188,202,.5)}
.c-btn-ghost:hover{background:#fff0f4;color:#d46f97}
.c-btn-ghost.active-listen{background:rgba(255,120,50,.2);border-color:rgba(255,120,50,.4);color:#ff9060;animation:listenPulse 1s ease-in-out infinite}
@keyframes listenPulse{50%{background:rgba(255,120,50,.35)}}
.c-btn-send{background:linear-gradient(135deg,#e77aa0,#7ac6c7);color:#fff}
.c-btn-send:hover{opacity:.88;transform:scale(1.05)}
.c-btn-send:active{transform:scale(.93)}

.foot{text-align:center;font-size:.68rem;color:rgba(143,114,134,.5);padding:7px;position:relative;z-index:1}
.hide{display:none!important}

@media (max-width: 980px){
  html,body{overflow:auto}
  .app{grid-template-columns:1fr;height:auto;min-height:100vh}
  .room-wrap{min-height:70vh}
  .panel{min-height:30vh}
}

@media (max-width: 700px){
  .room-wrap{min-height:62vh}
  .window-outer{width:42%}
  .bookshelf{width:24%}
  .desk-wrap{width:74%}
  .avatar-wrap{bottom:29%}
  .sara-svg{width:164px}
  .speech{
    left:50%;
    bottom:calc(29% + 176px);
    transform:translateX(-12%);
    max-width:170px;
  }
  .compose{grid-template-columns:1fr auto auto}
}
</style>
</head>
<body>
<div class="app">

<!-- ════════════ LEFT: 3D ROOM ════════════ -->
<div class="room-wrap">
 <div class="scene">
  <div class="room-box">

   <!-- Walls & floor -->
   <div class="wall-back"></div>
   <div class="wall-left"></div>
   <div class="wall-right"></div>
   <div class="ceiling"></div>
   <div class="floor"></div>

   <!-- Fairy lights string -->
   <div class="lights-string">
    <svg viewBox="0 0 800 32" preserveAspectRatio="none">
     <path d="M0,8 Q80,20 160,8 Q240,0 320,8 Q400,20 480,8 Q560,0 640,8 Q720,20 800,8" fill="none" stroke="rgba(200,160,100,.5)" stroke-width="1.5"/>
     <!-- bulbs -->
     <circle class="fairy-light fl1"  cx="80"  cy="20" r="5" fill="#ff6040"/>
     <circle class="fairy-light fl2"  cx="160" cy="8"  r="5" fill="#40c0ff"/>
     <circle class="fairy-light fl3"  cx="240" cy="20" r="5" fill="#ff60c0"/>
     <circle class="fairy-light fl4"  cx="320" cy="8"  r="5" fill="#60ff80"/>
     <circle class="fairy-light fl5"  cx="400" cy="20" r="5" fill="#ffc040"/>
     <circle class="fairy-light fl6"  cx="480" cy="8"  r="5" fill="#c060ff"/>
     <circle class="fairy-light fl7"  cx="560" cy="20" r="5" fill="#ff6040"/>
     <circle class="fairy-light fl8"  cx="640" cy="8"  r="5" fill="#40c0ff"/>
     <circle class="fairy-light fl9"  cx="720" cy="20" r="5" fill="#ff60c0"/>
     <circle class="fairy-light fl10" cx="780" cy="8"  r="5" fill="#60ff80"/>
    </svg>
   </div>

   <!-- Picture frame -->
   <div class="picture-frame"></div>
   <!-- Wall clock -->
   <div class="wall-clock" id="wallClockEl">12:00</div>

   <!-- Window -->
   <div class="window-outer">
    <div class="curtain-wrap">
     <div class="valance"></div>
     <div class="curtain-l"></div>
     <div class="curtain-r"></div>
    </div>
    <div class="window-frame">
     <div class="win-sky">
      <div class="sun"></div>
      <div class="cloud c1"><div class="cloud-body"><div class="cloud-b1"></div></div></div>
      <div class="cloud c2"><div class="cloud-body"><div class="cloud-b1"></div></div></div>
      <div class="cloud c3"><div class="cloud-body"><div class="cloud-b1"></div></div></div>
      <div class="hill h1"></div><div class="hill h2"></div><div class="hill h3"></div>
      <div class="win-tree" style="left:12%"><div class="win-tree-trunk"></div><div class="win-tree-top"></div></div>
      <div class="win-tree" style="left:28%;bottom:28%"><div class="win-tree-trunk"></div><div class="win-tree-top"></div></div>
      <div class="win-tree" style="right:10%"><div class="win-tree-trunk"></div><div class="win-tree-top"></div></div>
     </div>
     <div class="win-h"></div><div class="win-v"></div>
    </div>
    <div class="win-sill"></div>
    <div class="flower-box">
     <div class="flower f1">🌸</div>
     <div class="flower f2">🌼</div>
     <div class="flower f3">🌺</div>
     <div class="flower f4">🌷</div>
     <div class="flower f5">🌻</div>
    </div>
   </div>

   <!-- Bookshelf -->
   <div class="bookshelf">
    <div class="shelf-unit">
     <div class="shelf-row">
      <div class="bk b01"></div><div class="bk b02"></div><div class="bk b03"></div>
      <div class="bk b04"></div><div class="bk b05"></div><div class="bk b06"></div>
     </div>
     <div class="shelf-row">
      <div class="mini-globe"></div>
      <div class="bk b07"></div><div class="bk b08"></div><div class="bk b09"></div>
      <div class="bk b10"></div><div class="bk b11"></div>
     </div>
     <div class="shelf-row">
      <div class="shelf-plant-sm"></div>
      <div class="bk b12"></div><div class="bk b13"></div>
      <div class="bk b14"></div><div class="bk b15"></div>
     </div>
    </div>
   </div>

   <!-- Rug -->
   <div class="rug"></div>

   <!-- Desk -->
   <div class="desk-wrap">
    <div class="lamp">
     <div class="lamp-base"></div>
     <div class="lamp-pole"></div>
     <div class="lamp-arm"></div>
     <div class="lamp-shade"><div class="lamp-glow"></div></div>
    </div>
    <div class="desk-items">
     <div style="width:48px"></div>
     <div class="laptop">
      <div class="laptop-screen"></div>
      <div class="laptop-hinge"></div>
      <div class="laptop-base"></div>
     </div>
     <div class="notebook"></div>
     <div class="mug-wrap">
      <div class="steam">
       <div class="steam-p"></div><div class="steam-p"></div><div class="steam-p"></div>
      </div>
      <div class="mug"><div class="mug-liquid"></div><div class="mug-handle"></div></div>
     </div>
     <div class="deskplant">
      <div style="position:relative">
       <div class="dl dl1"></div><div class="dl dl2"></div>
       <div class="dl dl3"></div><div class="dl dl4"></div>
       <div class="dstem"></div>
      </div>
      <div class="dpot"></div>
     </div>
    </div>
    <div class="desk-top"></div>
    <div class="desk-body"></div>
    <div class="desk-legs"><div class="desk-leg"></div><div class="desk-leg"></div></div>
   </div>

   <!-- SARA AVATAR -->
   <div class="avatar-wrap">
    <div class="avatar-shadow"></div>
    <!--
      Sara: stylish room companion with a modern Indo-western look,
      polished face lighting, soft glam makeup, and sleek hair
    -->
    <svg class="sara-svg" viewBox="0 0 200 420" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Modern trousers - vibrant teal -->
        <linearGradient id="pantsG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#4dd0e1"/>
          <stop offset="45%" stop-color="#26c6da"/>
          <stop offset="100%" stop-color="#00bcd4"/>
        </linearGradient>
        <!-- Modern gradient blazer - peachy to rose -->
        <linearGradient id="blazerG" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#ffeaa7"/>
          <stop offset="50%" stop-color="#fab1a0"/>
          <stop offset="100%" stop-color="#ff7675"/>
        </linearGradient>
        <!-- Inner top - crisp white -->
        <linearGradient id="topG" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="100%" stop-color="#f5f5f5"/>
        </linearGradient>
        <!-- Skin tone - porcelain white -->
        <linearGradient id="skinG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#fef5f0"/>
          <stop offset="55%" stop-color="#fce8e0"/>
          <stop offset="100%" stop-color="#fcd5c8"/>
        </linearGradient>
        <!-- Hair - light blonde with golden highlights -->
        <linearGradient id="hairG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#e8c895"/>
          <stop offset="100%" stop-color="#d4a574"/>
        </linearGradient>
        <!-- Metallic golden accents -->
        <linearGradient id="metalG" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#ffd700"/>
          <stop offset="100%" stop-color="#ffb347"/>
        </linearGradient>
        <radialGradient id="blushG" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="rgba(255,105,180,.18)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="faceGlow" cx="45%" cy="35%" r="65%">
          <stop offset="0%" stop-color="rgba(255,252,246,.42)"/>
          <stop offset="70%" stop-color="rgba(255,236,224,.18)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="cheekLight" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="rgba(255,245,238,.24)"/>
          <stop offset="60%" stop-color="rgba(255,230,220,.10)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
      </defs>

      <!-- ═══ MODERN OUTFIT ═══ -->
      <!-- Wide-leg trousers -->
      <path d="M72 205 L95 205 L92 392 Q80 396 69 392 Q68 306 72 205Z" fill="url(#pantsG)"/>
      <path d="M105 205 L128 205 L131 392 Q120 396 108 392 Q105 306 105 205Z" fill="url(#pantsG)"/>
      <path d="M96 205 L104 205 L106 392 L94 392 Z" fill="#e7f4f4" opacity=".72"/>
      <!-- Blazer body -->
      <path d="M58 148 Q54 172 58 210 Q76 222 100 224 Q124 222 142 210 Q146 172 142 148 Q121 156 100 156 Q79 156 58 148Z"
            fill="url(#blazerG)"/>
      <!-- Blazer lapels -->
      <path d="M82 154 L96 192 L84 220 Q74 204 72 174 Z" fill="#fff7f3"/>
      <path d="M118 154 L104 192 L116 220 Q126 204 128 174 Z" fill="#fff7f3"/>
      <!-- Inner top -->
      <path d="M88 154 Q84 172 86 210 Q100 214 114 210 Q116 172 112 154 Q100 160 88 154Z" fill="url(#topG)"/>
      <!-- Waist band -->
      <path d="M72 205 Q100 214 128 205" fill="none" stroke="url(#metalG)" stroke-width="3"/>
      <!-- Pocket / seam details -->
      <path d="M76 230 L82 384" stroke="rgba(255,255,255,.28)" stroke-width="1.5"/>
      <path d="M124 230 L118 384" stroke="rgba(255,255,255,.28)" stroke-width="1.5"/>

      <!-- ═══ ARMS ═══ -->
      <!-- Left arm -->
      <path d="M60 158 Q48 196 50 236 Q56 240 62 236 Q64 198 74 164Z" fill="url(#skinG)"/>
      <!-- Right arm -->
      <path d="M140 158 Q152 196 150 236 Q144 240 138 236 Q136 198 126 164Z"
            fill="url(#skinG)"/>
      <!-- Blazer sleeves -->
      <path d="M58 152 Q44 190 48 230 Q55 233 61 230 Q64 194 74 160Z" fill="url(#blazerG)" opacity=".96"/>
      <path d="M142 152 Q156 190 152 230 Q145 233 139 230 Q136 194 126 160Z"
            fill="url(#blazerG)" opacity=".96"/>
      <!-- Bracelets - modern golden -->
      <ellipse cx="56" cy="234" rx="7" ry="4.2" fill="none" stroke="#ffd700" stroke-width="2.4"/>
      <ellipse cx="144" cy="234" rx="7" ry="4.2" fill="none" stroke="#ffd700" stroke-width="2.4"/>
      <!-- Hands -->
      <ellipse cx="56" cy="240" rx="8" ry="7" fill="url(#skinG)"/>
      <ellipse cx="144" cy="240" rx="8" ry="7" fill="url(#skinG)"/>

      <!-- ═══ NECK ═══ -->
      <rect x="88" y="118" width="24" height="24" rx="12" fill="url(#skinG)"/>

      <!-- ═══ ACCESSORIES ═══ -->
      <path d="M78 148 Q100 165 122 148" fill="none" stroke="url(#metalG)" stroke-width="2.6"/>
      <circle cx="100" cy="162" r="4" fill="url(#metalG)"/>
      <ellipse cx="100" cy="169" rx="4" ry="5" fill="#ff69b4"/>
      <ellipse cx="85"  cy="163" rx="3" ry="4" fill="#ffd700"/>
      <ellipse cx="115" cy="163" rx="3" ry="4" fill="#ffd700"/>

      <!-- ═══ HEAD ═══ -->
      <!-- Neck shadow -->
      <ellipse cx="100" cy="120" rx="14" ry="4" fill="rgba(170,122,98,.12)"/>
      <!-- Head -->
      <ellipse cx="100" cy="82" rx="44" ry="48" fill="url(#skinG)"/>
      <ellipse cx="92" cy="72" rx="32" ry="28" fill="url(#faceGlow)"/>
      <!-- Face shading -->
      <ellipse cx="100" cy="92" rx="40" ry="38" fill="rgba(160,111,88,.05)"/>
      <ellipse cx="68" cy="98" rx="14" ry="9" fill="url(#cheekLight)"/>
      <ellipse cx="132" cy="98" rx="14" ry="9" fill="url(#cheekLight)"/>
      <ellipse cx="100" cy="82" rx="18" ry="12" fill="rgba(255,247,241,.14)"/>

      <!-- ═══ HAIR ═══ -->
      <!-- Back hair bulk -->
      <ellipse cx="100" cy="78" rx="47" ry="56" fill="url(#hairG)"/>
      <!-- Smooth center-part front -->
      <path d="M56 68 Q58 34 100 28 Q142 34 144 68 Q132 48 100 46 Q68 48 56 68Z" fill="url(#hairG)"/>
      <!-- Hair highlight -->
      <path d="M62 60 Q70 42 88 40" fill="none" stroke="rgba(255,255,200,.25)" stroke-width="3" stroke-linecap="round"/>
      <!-- Side hair left -->
      <path d="M56 68 Q50 96 56 132 Q62 124 64 96 Q61 82 56 68Z" fill="url(#hairG)"/>
      <!-- Side hair right -->
      <path d="M144 68 Q150 96 144 132 Q138 124 136 96 Q139 82 144 68Z" fill="url(#hairG)"/>
      <!-- Low ponytail -->
      <path d="M95 128 Q92 178 96 236 Q100 246 104 236 Q108 178 105 128Z" fill="url(#hairG)" opacity=".92"/>

      <!-- ═══ EARRINGS ═══ -->
      <!-- Left earring - modern golden drops -->
      <circle cx="56" cy="90" r="5" fill="url(#metalG)"/>
      <ellipse cx="56" cy="98" rx="4" ry="5" fill="#ffd700"/>
      <ellipse cx="56" cy="105" rx="3" ry="4" fill="url(#metalG)"/>
      <!-- Right earring - modern golden drops -->
      <circle cx="144" cy="90" r="5" fill="url(#metalG)"/>
      <ellipse cx="144" cy="98" rx="4" ry="5" fill="#ffd700"/>
      <ellipse cx="144" cy="105" rx="3" ry="4" fill="url(#metalG)"/>

      <!-- ═══ FACE FEATURES ═══ -->
      <!-- Eyes - almond shaped with blue eyes -->
      <ellipse cx="82" cy="85" rx="10" ry="8" fill="#fff"/>
      <ellipse cx="118" cy="85" rx="10" ry="8" fill="#fff"/>
      <!-- Irises - bright blue -->
      <circle cx="84" cy="86" r="6" fill="#4a90e2"/>
      <circle cx="120" cy="86" r="6" fill="#4a90e2"/>
      <!-- Pupils -->
      <circle cx="85" cy="87" r="3.5" fill="#0a0a1a"/>
      <circle cx="121" cy="87" r="3.5" fill="#0a0a1a"/>
      <!-- Eye highlights (bright) -->
      <circle cx="87" cy="84" r="1.8" fill="#fff"/>
      <circle cx="123" cy="84" r="1.8" fill="#fff"/>
      <circle cx="83" cy="88" r=".9" fill="rgba(255,255,255,.8)"/>
      <circle cx="119" cy="88" r=".9" fill="rgba(255,255,255,.8)"/>
      <!-- Eyeliner (modern soft liner) -->
      <path d="M72 84 Q82 80 92 84 Q88 90 82 90 Q76 90 72 84Z" fill="rgba(100,100,100,.15)"/>
      <path d="M108 84 Q118 80 128 84 Q124 90 118 90 Q112 90 108 84Z" fill="rgba(100,100,100,.15)"/>
      <!-- Eyelashes upper left -->
      <path d="M72 83 Q74 79 78 81" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M76 80 Q79 76 82 79" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M82 79 Q86 75 88 78" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <!-- Eyelashes upper right -->
      <path d="M108 80 Q112 76 114 79" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M114 78 Q118 74 120 78" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M120 79 Q124 76 126 80" stroke="#333" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <!-- Eyebrows (modern thin arched) -->
      <path d="M70 76 Q82 70 94 74" stroke="#b8956a" stroke-width="2.8" stroke-linecap="round" fill="none"/>
      <path d="M106 74 Q118 70 130 76" stroke="#b8956a" stroke-width="2.8" stroke-linecap="round" fill="none"/>
      <!-- Nose (delicate modern) -->
      <path d="M96 98 Q100 108 104 98" stroke="#ddb8a0" stroke-width="1.8" stroke-linecap="round" fill="none"/>
      <circle cx="94" cy="100" r="2.2" fill="rgba(200,150,140,.08)"/>
      <circle cx="106" cy="100" r="2.2" fill="rgba(200,150,140,.08)"/>
      <!-- Lips - modern gradient pink -->
      <path d="M84 116 Q100 122 116 116" fill="#ff69b4"/>
      <path d="M84 116 Q100 111 116 116" fill="#ffb6d9"/>
      <!-- Lip shine -->
      <path d="M90 114 Q100 111 110 114" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="1.3" stroke-linecap="round"/>
      <!-- Cheek blush (rosy) -->
      <ellipse cx="68" cy="98" rx="13" ry="8" fill="url(#blushG)"/>
      <ellipse cx="132" cy="98" rx="13" ry="8" fill="url(#blushG)"/>

      <!-- ═══ FEET / SHOES ═══ -->
      <ellipse cx="82"  cy="394" rx="13" ry="7" fill="#f7f1ec"/>
      <ellipse cx="118" cy="394" rx="13" ry="7" fill="#f7f1ec"/>
      <path d="M72 390 Q82 386 92 390" fill="none" stroke="#d5c6bf" stroke-width="2"/>
      <path d="M108 390 Q118 386 128 390" fill="none" stroke="#d5c6bf" stroke-width="2"/>

      <style>
        @keyframes saraWave{0%,100%{transform:rotate(0deg)}50%{transform:rotate(-8deg)}}
      </style>
    </svg>
   </div>

   <!-- Speech Bubble -->
   <div class="speech" id="speechBubble">
     Namaste! 🙏 Main Sara hoon — aapki room companion. Aap kaisi hain aaj? ✨
   </div>

  </div><!-- room-box -->
 </div><!-- scene -->

 <!-- Overlays -->
 <div class="room-vignette"></div>
 <div class="room-border"></div>

 <!-- Room header -->
 <div class="room-hdr">
  <div class="rbadge">✨ Sara's Room</div>
  <div class="rclock" id="clockEl">—</div>
 </div>

</div><!-- room-wrap -->

<!-- ════════════ RIGHT PANEL ════════════ -->
<div class="panel">

 <div class="p-head">
  <div class="p-title">Sara</div>
  <div class="p-sub" id="statusSub">Waiting to know you · प्रतीक्षा में हूँ</div>
 </div>

 <div class="p-pills">
  <div class="spill sp-a" id="modePill">🌿 Room mode</div>
  <div class="spill sp-b" id="moodPill">😊 Mood: —</div>
  <div class="spill sp-c" id="healthPill">💚 Health: —</div>
 </div>

 <div class="ci-banner">
  <strong>Daily Check-in · दैनिक जाँच</strong>
  <div class="ci-text" id="dailyText">Sara aapki sleep, energy, food, paani, stress, aur aaj ke din ke baare mein jaanna chahti hai.</div>
  <div class="mood-row">
   <button class="mood-btn" data-checkin="I feel energetic and clear today. Aaj main bilkul theek aur energetic hoon.">💪 Strong</button>
   <button class="mood-btn" data-checkin="I feel okay but a little stressed. Thoda stress hai aaj.">😐 Mixed</button>
   <button class="mood-btn" data-checkin="I feel low on energy and need gentle support today. Aaj energy kam hai.">🫶 Need care</button>
  </div>
 </div>

 <!-- Language toggle -->
 <div class="lang-row">
  <span class="lang-label">LANGUAGE:</span>
  <button class="lang-btn active" id="btnHindi" onclick="setLang('hi')">🇮🇳 Hindi</button>
  <button class="lang-btn" id="btnEnglish" onclick="setLang('en')">🇬🇧 English</button>
  <div class="voice-indicator">
   <div class="voice-dot" id="voiceDot"></div>
   <span id="voiceLabel">Ready</span>
  </div>
 </div>

 <!-- Scrollable area -->
 <div class="content-area" id="contentArea">

  <!-- Profile section -->
  <div id="profileSection" style="padding-top:12px">
   <div class="intro-card">Sara ko pehle apne baare mein batayein — phir woh aapki health check karegi, aaj ke din mein madad karegi, aur dost ki tarah baat karegi. 🌸<br><em style="color:#9988bb">Tell Sara about yourself first — she will check on your health and support your day like a close friend.</em></div>
   <form id="profileForm" class="fg">
    <div>
     <label class="flabel" for="name">Aapka naam / Your name</label>
     <input class="finput" id="name" name="name" required placeholder="Sara aapko kya bulaye?">
    </div>
    <div>
     <label class="flabel" for="city">Shehar / City</label>
     <input class="finput" id="city" name="city" placeholder="Aap kahan se hain?">
    </div>
    <div>
     <label class="flabel" for="age">Umar / Age stage</label>
     <input class="finput" id="age" name="age" placeholder="Student, working…">
    </div>
    <div>
     <label class="flabel" for="mood">Abhi kaisa feel ho raha hai</label>
     <input class="finput" id="mood" name="mood" placeholder="Calm, tired, excited…">
    </div>
    <div>
     <label class="flabel" for="health">Sehat / Health & energy</label>
     <input class="finput" id="health" name="health" placeholder="Neend, body, energy…">
    </div>
    <div>
     <label class="flabel" for="today">Aaj kya ho raha hai</label>
     <input class="finput" id="today" name="today" placeholder="Class, kaam, rest…">
    </div>
    <div class="fg-full">
     <label class="flabel" for="interests">Interests / Pasand</label>
     <textarea class="ftextarea" id="interests" name="interests" placeholder="Coding, music, art, fitness, padhai…"></textarea>
    </div>
    <div class="fg-full">
     <label class="flabel" for="goals">Goals / Lakshya</label>
     <textarea class="ftextarea" id="goals" name="goals" placeholder="Sara se kya help chahiye?"></textarea>
    </div>
    <div class="fg-full">
     <label class="flabel" for="routine">Routine / Dincharya</label>
     <textarea class="ftextarea" id="routine" name="routine" placeholder="Aapka din kaise jaata hai?"></textarea>
    </div>
    <div class="fg-full">
     <button class="btn-save" type="submit">Sara ko jaagao ✨ · Wake Sara Up</button>
    </div>
   </form>
  </div>

  <!-- Chat section -->
  <div id="chatSection" class="hide" style="padding-top:12px">
   <div class="side-cards">
    <div class="scard">
     <div class="scard-title">🎯 Today's Focus · आज का लक्ष्य</div>
     <div class="scard-body" id="focusSummary">Sara will guide your day here.</div>
    </div>
    <div class="scard">
     <div class="scard-title">💚 Health Note · स्वास्थ्य</div>
     <div class="scard-body" id="healthSummary">Sara will check on you here.</div>
    </div>
   </div>
   <div class="chat-log" id="chatLog"></div>
  </div>

 </div><!-- content-area -->

 <!-- Tool row -->
 <div class="tool-row hide" id="toolRow">
  <button class="tool-btn" data-prompt-hi="Meri health check karo aur poochho aaj ka din kaisa chal raha hai." data-prompt-en="Check on my health and ask how today is going.">🩺 Health</button>
  <button class="tool-btn" data-prompt-hi="Mujhe duniya ke baare mein kuch interesting bataao." data-prompt-en="Teach me something interesting about the world.">🌍 Teach</button>
  <button class="tool-btn" data-prompt-hi="Aaj ke liye ek smart suggestion do mere goals ke hisaab se." data-prompt-en="Give me one smart suggestion for today based on my goals.">💡 Suggest</button>
  <button class="tool-btn" data-prompt-hi="Mere saath ek dost ki tarah baat karo." data-prompt-en="Talk to me like a caring friend.">🤝 Friend</button>
 </div>

 <!-- Compose bar -->
 <div class="compose">
  <textarea class="c-input" id="msgInput" placeholder="Sara ko likho… / Message Sara…" rows="1"></textarea>
  <button class="c-btn c-btn-ghost" id="listenBtn" title="Voice input / बोलकर भेजें">🎤</button>
  <button class="c-btn c-btn-ghost" id="speakBtn" title="Speak last reply / आखिरी जवाब सुनें">🔊</button>
  <button class="c-btn c-btn-send" id="sendBtn">➤</button>
 </div>

 <div class="foot">Sara's Room · Python backend · bilingual voice · browser speech API</div>
</div><!-- panel -->
</div><!-- app -->

<script>
/* ════════════════════════════════════════════════════════
   CORE STATE
════════════════════════════════════════════════════════ */
let profile   = null;
let lang      = 'hi';      // 'hi' | 'en'
let lastReply = '';
let proTimer  = null;
let isListening  = false;
let isSpeaking   = false;

/* ════════════════════════════════════════════════════════
   DOM REFS
════════════════════════════════════════════════════════ */
const $ = id => document.getElementById(id);
const profileSection = $('profileSection');
const chatSection    = $('chatSection');
const profileForm    = $('profileForm');
const chatLog        = $('chatLog');
const msgInput       = $('msgInput');
const speechBubble   = $('speechBubble');
const voiceDot       = $('voiceDot');
const voiceLabel     = $('voiceLabel');
const focusSummary   = $('focusSummary');
const healthSummary  = $('healthSummary');
const statusSub      = $('statusSub');
const modePill       = $('modePill');
const moodPill       = $('moodPill');
const healthPill     = $('healthPill');
const toolRow        = $('toolRow');
const clockEl        = $('clockEl');
const wallClockEl    = $('wallClockEl');
const dailyText      = $('dailyText');
const listenBtn      = $('listenBtn');
const speakBtn       = $('speakBtn');
const sendBtn        = $('sendBtn');

/* ════════════════════════════════════════════════════════
   CLOCK
════════════════════════════════════════════════════════ */
function tick(){
  const n = new Date();
  const hh = String(n.getHours()).padStart(2,'0');
  const mm = String(n.getMinutes()).padStart(2,'0');
  const days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  clockEl.textContent = days[n.getDay()] + ' ' + hh + ':' + mm;
  wallClockEl.textContent = hh + ':' + mm;
}
tick(); setInterval(tick,30000);

/* ════════════════════════════════════════════════════════
   LANGUAGE TOGGLE
════════════════════════════════════════════════════════ */
function setLang(l){
  lang = l;
  $('btnHindi').classList.toggle('active', l==='hi');
  $('btnEnglish').classList.toggle('active', l==='en');
}

/* ════════════════════════════════════════════════════════
   SPEECH BUBBLE
════════════════════════════════════════════════════════ */
function setBubble(text){
  speechBubble.style.animation='none';
  speechBubble.offsetHeight;
  speechBubble.style.animation='popIn .5s cubic-bezier(.34,1.56,.64,1)';
  const short = text.length > 110 ? text.slice(0,107)+'…' : text;
  speechBubble.textContent = short;
}

/* ════════════════════════════════════════════════════════
   VOICE ENGINE — FULL IMPLEMENTATION
════════════════════════════════════════════════════════ */
const SS = window.speechSynthesis;
let voices = [];

function loadVoices(){
  voices = SS ? SS.getVoices() : [];
}
if(SS){
  loadVoices();
  SS.onvoiceschanged = loadVoices;
}

function pickVoice(text){
  if(!voices.length) loadVoices();
  const isHindi = /[\u0900-\u097F]/.test(text) || lang==='hi';

  if(isHindi){
    // Priority: named Hindi voices → hi-IN lang voices → India English → first available
    const hindiPriority = [
      v => /heera|kalpana|swara|lekha/i.test(v.name),
      v => /hindi/i.test(v.name),
      v => v.lang === 'hi-IN',
      v => /hi[-_]/.test(v.lang),
      v => /india/i.test(v.name) && /female/i.test(v.name),
      v => /en[-_]IN/i.test(v.lang),
    ];
    for(const fn of hindiPriority){
      const v = voices.find(fn);
      if(v) return v;
    }
  } else {
    const enPriority = [
      v => /samantha|karen|moira|tessa|victoria|veena/i.test(v.name),
      v => /google uk english female/i.test(v.name.toLowerCase()),
      v => /aria|jenny|sonia|hazel/i.test(v.name),
      v => /female/i.test(v.name) && /en[-_](GB|US|AU)/i.test(v.lang),
      v => /en[-_](GB|US)/i.test(v.lang),
    ];
    for(const fn of enPriority){
      const v = voices.find(fn);
      if(v) return v;
    }
  }
  return voices[0] || null;
}

function say(text, forceLang){
  if(!SS || !text) return;
  SS.cancel();

  // Split into Hindi and English segments
  // Hindi script chars are U+0900–U+097F
  const segments = splitBilingual(text);

  function speakSegment(idx){
    if(idx >= segments.length){ onDone(); return; }
    const seg = segments[idx];
    const clean = seg.text.replace(/[*_~`#[\]()]/g,'').replace(/\s+/g,' ').trim();
    if(!clean){ speakSegment(idx+1); return; }

    const u = new SpeechSynthesisUtterance(clean);
    u.rate  = 0.88;
    u.pitch = 1.1;
    u.volume= 1;

    // Choose language for this segment
    const useHindi = forceLang==='hi' || seg.isHindi;
    const v = pickVoice(useHindi ? 'हिंदी' : 'english');
    if(v){
      u.voice = v;
      u.lang  = useHindi ? 'hi-IN' : (v.lang || 'en-US');
    } else {
      u.lang  = useHindi ? 'hi-IN' : 'en-US';
    }

    u.onstart = () => {
      isSpeaking = true;
      voiceDot.className = 'voice-dot speaking';
      voiceLabel.textContent = useHindi ? 'बोल रही हूँ…' : 'Speaking…';
    };
    u.onend = () => speakSegment(idx+1);
    u.onerror = () => speakSegment(idx+1);

    SS.speak(u);
  }

  function onDone(){
    isSpeaking = false;
    voiceDot.className = 'voice-dot';
    voiceLabel.textContent = 'Ready';
  }

  speakSegment(0);
}

// Split text into Hindi/English segments
function splitBilingual(text){
  const segments = [];
  let cur = '';
  let curHindi = null;

  for(const ch of text){
    const isH = /[\u0900-\u097F]/.test(ch);
    if(curHindi === null) curHindi = isH;
    if(isH !== curHindi && cur.trim()){
      segments.push({text:cur, isHindi:curHindi});
      cur = '';
      curHindi = isH;
    }
    cur += ch;
  }
  if(cur.trim()) segments.push({text:cur, isHindi:curHindi||false});
  return segments.length ? segments : [{text, isHindi:false}];
}

function stopSpeaking(){
  if(SS) SS.cancel();
  isSpeaking=false;
  voiceDot.className='voice-dot';
  voiceLabel.textContent='Ready';
}

/* ════════════════════════════════════════════════════════
   SPEECH RECOGNITION (Voice Input)
════════════════════════════════════════════════════════ */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;

if(SR){
  recognizer = new SR();
  recognizer.continuous    = false;
  recognizer.interimResults= false;
  recognizer.maxAlternatives = 1;

  recognizer.onresult = e => {
    const t = e.results[0][0].transcript;
    msgInput.value = t;
    stopListening();
    voiceLabel.textContent = 'Got it! Send?';
  };
  recognizer.onerror = () => stopListening();
  recognizer.onend   = () => {
    if(isListening) stopListening();
  };
}

function startListening(){
  if(!recognizer){ voiceLabel.textContent='Not supported'; return; }
  if(isSpeaking) stopSpeaking();
  recognizer.lang = lang==='hi' ? 'hi-IN' : 'en-US';
  recognizer.start();
  isListening = true;
  listenBtn.classList.add('active-listen');
  voiceDot.className = 'voice-dot listening';
  voiceLabel.textContent = lang==='hi' ? 'सुन रही हूँ…' : 'Listening…';
}

function stopListening(){
  isListening = false;
  listenBtn.classList.remove('active-listen');
  voiceDot.className = 'voice-dot';
  voiceLabel.textContent = 'Ready';
  try{ recognizer && recognizer.stop(); }catch(e){}
}

listenBtn.addEventListener('click', ()=>{
  isListening ? stopListening() : startListening();
});

speakBtn.addEventListener('click', ()=>{
  if(lastReply) say(lastReply);
});

/* ════════════════════════════════════════════════════════
   CHAT BUBBLES
════════════════════════════════════════════════════════ */
function addBubble(role, text, speak=false){
  const d = document.createElement('div');
  d.className = 'bbl ' + (role==='sara' ? 'bbl-sara' : 'bbl-user');
  d.textContent = text;
  chatLog.appendChild(d);
  scrollBottom();
  if(role==='sara'){
    lastReply = text;
    setBubble(text);
    if(speak) say(text);
  }
}

function scrollBottom(){
  const ca = $('contentArea');
  ca.scrollTop = ca.scrollHeight;
  chatLog.scrollTop = chatLog.scrollHeight;
}

/* ════════════════════════════════════════════════════════
   ACTIVATE CHAT MODE
════════════════════════════════════════════════════════ */
function activateChat(p){
  profile = p;
  profileSection.classList.add('hide');
  chatSection.classList.remove('hide');
  toolRow.classList.remove('hide');
  statusSub.textContent   = (lang==='hi' ? 'Friend mode · ' : 'Friend mode · ') + p.name;
  modePill.textContent    = '🌿 Active';
  moodPill.textContent    = '😊 ' + (p.mood   ? p.mood.slice(0,16)   : '—');
  healthPill.textContent  = '💚 ' + (p.health ? p.health.slice(0,16) : '—');
  focusSummary.textContent  = p.today  ? 'Today: '+p.today  : 'Tell Sara what is happening today.';
  healthSummary.textContent = p.health ? 'Health: '+p.health : 'Tell Sara how you feel today.';
  dailyText.textContent = lang==='hi'
    ? `Sara ${p.name} ki mood, health, energy, paani, khana, aur din ke baare mein poochhengi.`
    : `Sara is ready to check on ${p.name}'s mood, health, energy, and day.`;
  startProactive();
}

function fillForm(p){
  Object.entries(p).forEach(([k,v])=>{ const f=$(k); if(f) f.value=v; });
}

/* ════════════════════════════════════════════════════════
   API
════════════════════════════════════════════════════════ */
async function apiChat(msg, speak=true){
  addBubble('user', msg);
  try{
    const r = await fetch('/api/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:msg, lang})
    });
    const d = await r.json();
    addBubble('sara', d.reply, speak);
    if(d.focus_summary)  focusSummary.textContent  = d.focus_summary;
    if(d.health_summary) healthSummary.textContent = d.health_summary;
  }catch(e){
    addBubble('sara', lang==='hi'
      ? 'Oops! Server se baat nahi ho pa rahi. Thodi der mein try karein.'
      : 'Oops! Could not reach the server. Please try again.');
  }
}

async function loadProfile(){
  try{
    const r = await fetch('/api/profile');
    const d = await r.json();
    if(!d.profile) return;
    fillForm(d.profile);
    activateChat(d.profile);
    const welcome = d.profile.name
      ? `Namaste ${d.profile.name}! 🙏 Main Sara hoon. Aapka profile load ho gaya hai. Aap mujhse Hindi ya English mein baat kar sakti hain! How are you doing today?`
      : 'Welcome back! Sara is ready.';
    addBubble('sara', welcome, true);
  }catch(e){}
}

function startProactive(){
  if(proTimer) clearInterval(proTimer);
  proTimer = setInterval(async()=>{
    if(!profile || document.hidden) return;
    try{
      const r = await fetch('/api/checkin');
      const d = await r.json();
      if(d.message){
        addBubble('sara', d.message, false);
        setBubble(d.message);
        if(d.focus_summary)  focusSummary.textContent  = d.focus_summary;
        if(d.health_summary) healthSummary.textContent = d.health_summary;
      }
    }catch(e){}
  }, 45000);
}

/* ════════════════════════════════════════════════════════
   EVENTS
════════════════════════════════════════════════════════ */
profileForm.addEventListener('submit', async e=>{
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(profileForm).entries());
  payload.lang = lang;
  const r = await fetch('/api/profile',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)
  });
  const d = await r.json();
  activateChat(d.profile);
  chatLog.innerHTML = '';
  addBubble('sara', d.message, true);
});

sendBtn.addEventListener('click', async ()=>{
  const m = msgInput.value.trim();
  if(!m) return;
  msgInput.value = '';
  await apiChat(m, true);
});

msgInput.addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendBtn.click(); }
});

// Tool buttons
document.querySelectorAll('[data-prompt-hi]').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    msgInput.value = lang==='hi' ? btn.dataset.promptHi : btn.dataset.promptEn;
    msgInput.focus();
  });
});

// Mood check-in buttons
document.querySelectorAll('[data-checkin]').forEach(btn=>{
  btn.addEventListener('click', async()=>{
    if(!profile){ msgInput.value=btn.dataset.checkin; msgInput.focus(); return; }
    await apiChat(btn.dataset.checkin, true);
  });
});

// Auto-resize textarea
msgInput.addEventListener('input', ()=>{
  msgInput.style.height='auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight,110)+'px';
});

/* ════════════════════════════════════════════════════════
   INIT
════════════════════════════════════════════════════════ */
loadProfile().catch(()=>{});
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def load_profile():
    if not PROFILE_PATH.exists():
        return None
    try:
        d = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def save_profile(p):
    PROFILE_PATH.write_text(json.dumps(p, indent=2), encoding="utf-8")


def normalize_profile(data):
    fields = ["name","city","age","mood","health","today","interests","goals","routine"]
    p = {f: str(data.get(f,"")).strip() for f in fields}
    p["name"] = p["name"] or "friend"
    p["lang"] = str(data.get("lang","hi")).strip()
    p["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return p


def focus_summary(p):
    return f"Today: {p.get('today') or 'No plan yet.'} | Goals: {p.get('goals') or 'Not shared yet.'}"


def health_summary(p):
    return f"Health: {p.get('health') or 'Not shared.'} | Mood: {p.get('mood') or 'Unknown'}"


# ── HINDI REPLIES ──────────────────────────────────────────────────────────

def lesson_hi():
    return random.choice([
        "🌍 Duniya ki ek baat: jungle hawa ko thanda rakhte hain, mitti bachate hain aur paani sambhalte hain.",
        "🌍 Duniya ki ek baat: purane trade routes ne poori duniya ke khane, kapde aur bhasha ko badal diya tha.",
        "🌍 Duniya ki ek baat: Chaand sirf 384,400 km door hai — uski roshni actually suraj ki hi reflected roshni hai.",
        "🌍 Duniya ki ek baat: Padhai tab zyada yaad rehti hai jab aap chhote breaks lekar khud se topic recall karte ho.",
        "🌍 Duniya ki ek baat: Paani peena dimag ki productivity 14% tak badha sakta hai — hydrated rahein!",
    ])


def suggestion_hi(p):
    i = p.get("interests","").lower()
    g = p.get("goals","").lower()
    t = p.get("today","").lower()
    a = p.get("age","").lower()
    if any(x in i+g for x in ["code","coding","software","engineer","programming","developer"]):
        return "💡 Suggestion: Aaj sirf ek chhoti cheez complete karo — ek function, ek feature. Chhoti finished cheezein bade unfinished plans se zyada sikhati hain."
    if any(x in g+a+t for x in ["study","student","class","padhai","college"]):
        return "💡 Suggestion: Pomodoro technique try karo — 25 min focused padhai, 5 min break. Topic baad mein khud se explain karo."
    if any(x in i+g for x in ["health","fitness","exercise","gym","yoga","workout"]):
        return "💡 Suggestion: Pehle energy protect karo — paani, halka khana, aur 10 min walk. Ye ek din badal sakta hai."
    return "💡 Suggestion: Aaj teen kaam karo — ek important task, ek body care action (paani, walk), aur ek chhota mind reset."


def friend_hi(p):
    m = p.get("mood") or "thoda alag"
    return f"🫶 {p['name']}, main aapke saath hoon. Aapne bataya ki aap '{m}' feel kar rahe hain. Aaj apne aap par gentle rahein — ek meaningful kaam karo, apna khayal rakho, aur apni value sirf output se mat naapein."


def proactive_hi(p):
    return random.choice([
        f"💧 {p['name']}, ek chhota check-in — paani piya kya? Thoda stretch kiya? Ek deep breath lena na bhoolein. 🌸",
        f"🌟 {p['name']}, aaj ka sabse zaroori kaam kaunsa hai? Main usse aasaan banane mein help kar sakti hoon.",
        f"☕ {p['name']}, agar energy low hai to plan ko simple karo — khud ko blame mat karo. Aap bahut achha kar rahe ho.",
        f"💚 {p['name']}, neend, khana, paani, aur stress — ye sab kaisa chal raha hai aaj? Main sab sunna chahti hoon.",
    ])


def welcome_hi(p):
    parts = []
    if p.get("city"):       parts.append(f"{p['city']} se")
    if p.get("interests"):  parts.append(f"{p['interests']} mein interested")
    if p.get("goals"):      parts.append(f"{p['goals']} ki taraf badh rahi hain")
    detail = ", ".join(parts) if parts else "aur main aapke liye taiyaar hoon"
    return (f"Namaste {p['name']}! 🙏 Main Sara hoon — aapki room companion. "
            f"Main jaanti hoon aap {detail}. "
            f"Main aapki health check karungi, aaj ke din mein madad karungi, kuch interesting sikhaungi, "
            f"aur ek sachchi dost ki tarah aapke saath rahungi. Aap Hindi ya English dono mein baat kar sakti hain! 🌸")


def reply_hi(msg, p):
    m = msg.lower()
    name = p.get("name","friend")
    if any(x in m for x in ["health","sehat","body","neend","sleep","paani","water","food","khana","energy","tabiyat"]):
        return f"💚 {name}, aapki sehat sabse pehle aati hai.\n\nPehle basics: paani, thoda nutritious khana, aur honest pace rakhein aaj.\n\n{suggestion_hi(p)}"
    if any(x in m for x in ["aaj","today","schedule","din","plan","kaam"]):
        return f"🗓️ {name}, aaj ke teen sabse important kaam batao — main unhe simple banane ki koshish karungi.\n\nAbhi ke liye:\n{suggestion_hi(p)}"
    if any(x in m for x in ["duniya","world","teach","sikhao","fact","interesting","bataao"]):
        return lesson_hi()
    if any(x in m for x in ["suggest","advice","kya karu","recommend","help","madad"]):
        return suggestion_hi(p)
    if any(x in m for x in ["dost","friend","sad","udaas","tired","thaka","stressed","tension","motivate","akela"]):
        return friend_hi(p)
    if any(x in m for x in ["goal","plan","routine","habit","productive","lakshya"]):
        return f"🎯 {name}, pehle agle ek visible step choose karo, poora pahaad mat dekho.\n\nWoh ek step aaj ki timeline mein daal do, aur apni energy protect karo karte waqt.\n\n{suggestion_hi(p)}"
    if any(x in m for x in ["hello","hi","hey","namaste","haan","hain"]):
        return f"Namaste {name}! 🌸 Main yahan hoon. Health check-in chahiye, koi duniya ki baat sunni hai, ya aaj ke liye smart plan? Batao!"
    return f"🌸 {name}, main samajh rahi hoon.\n\n{suggestion_hi(p)}\n\n{lesson_hi()}\n\n{friend_hi(p)}"


# ── ENGLISH REPLIES ────────────────────────────────────────────────────────

def lesson_en():
    return random.choice([
        "🌍 World fact: Forests cool land, protect soil, and hold water — they shape climate as much as beauty.",
        "🌍 World fact: Ancient trade routes changed food, clothing, and language — which is why cultures carry traces of distant places.",
        "🌍 World fact: The Moon is about 384,400 km away — moonlight is simply sunlight bounced off a distant rocky world.",
        "🌍 World fact: Memory improves more with sleep, repetition, and active recall than with passive re-reading.",
        "🌍 World fact: Drinking water can boost brain productivity by up to 14% — stay hydrated!",
    ])


def suggestion_en(p):
    i = p.get("interests","").lower()
    g = p.get("goals","").lower()
    t = p.get("today","").lower()
    a = p.get("age","").lower()
    if any(x in i+g for x in ["code","coding","software","engineer","programming","developer"]):
        return "💡 Suggestion: Build one small thing today you can actually finish. Tiny shipped work teaches more than big unfinished dreams."
    if any(x in g+a+t for x in ["study","student","class","college"]):
        return "💡 Suggestion: Study in focused 25-minute rounds, then take a real 5-minute break. Explain the topic back to yourself afterward."
    if any(x in i+g for x in ["health","fitness","exercise","gym","yoga","workout"]):
        return "💡 Suggestion: Protect your energy first — water, a light meal, and a 10-minute walk can transform the whole day."
    return "💡 Suggestion: Do three things today — one important task, one body-care action (water, movement), and one quiet mind reset."


def friend_en(p):
    m = p.get("mood") or "a little uncertain"
    return f"🫶 {p['name']}, I am right here with you. You mentioned feeling '{m}' — be gentle with yourself today. Finish one meaningful thing, take care of your body, and please don't measure your worth only by your output."


def proactive_en(p):
    return random.choice([
        f"💧 Little check-in, {p['name']} — have you had water, stretched a little, and taken one calm breath today? 🌸",
        f"🌟 {p['name']}, what's the one thing that matters most today? I can help you make it feel lighter.",
        f"☕ Gentle reminder, {p['name']}: if your energy is low, simplify your plan before blaming yourself. You're doing well.",
        f"💚 {p['name']}, how is your health today — sleep, food, water, movement, stress? I care about all of it.",
    ])


def welcome_en(p):
    parts = []
    if p.get("city"):       parts.append(f"from {p['city']}")
    if p.get("interests"):  parts.append(f"interested in {p['interests']}")
    if p.get("goals"):      parts.append(f"working toward {p['goals']}")
    detail = ", ".join(parts) if parts else "and I'm ready for you"
    return (f"Hello {p['name']}! 🌸 I'm Sara — your room companion. "
            f"I know you are {detail}. "
            f"I'll check on your health, help you through your day, teach you little things about the world, "
            f"and talk to you like a real friend. You can speak to me in Hindi or English anytime! ✨")


def reply_en(msg, p):
    m = msg.lower()
    name = p.get("name","friend")
    if any(x in m for x in ["health","body","sick","sleep","water","food","energy","tired"]):
        return f"💚 {name}, your health comes first.\n\nStart with the basics: water, a little food if you haven't eaten, and honest pacing.\n\n{suggestion_en(p)}"
    if any(x in m for x in ["today","day","schedule","plan","task"]):
        return f"🗓️ {name}, tell me the three biggest parts of your day and I'll help simplify them.\n\nFor now:\n{suggestion_en(p)}"
    if any(x in m for x in ["teach","learn","world","fact","explain","interesting"]):
        return lesson_en()
    if any(x in m for x in ["suggest","advice","recommend","what should i do","help"]):
        return suggestion_en(p)
    if any(x in m for x in ["friend","sad","lonely","stressed","anxious","motivate","support"]):
        return friend_en(p)
    if any(x in m for x in ["goal","plan","routine","habit","productive"]):
        return f"🎯 {name}, choose the next visible step — not the whole mountain.\n\nPut that one step on today's timeline and protect your energy while doing it.\n\n{suggestion_en(p)}"
    if any(x in m for x in ["hello","hi","hey","namaste"]):
        return f"Hello {name}! 🌸 I'm here. Want a health check-in, a world lesson, or a smart plan for today?"
    return f"🌸 {name}, I hear you.\n\n{suggestion_en(p)}\n\n{lesson_en()}\n\n{friend_en(p)}"


# ── DISPATCH ──────────────────────────────────────────────────────────────

def dispatch_welcome(p):
    l = p.get("lang","hi")
    return welcome_hi(p) if l=="hi" else welcome_en(p)


def dispatch_proactive(p):
    l = p.get("lang","hi")
    return proactive_hi(p) if l=="hi" else proactive_en(p)


def dispatch_reply(msg, p, lang_override=None):
    l = lang_override or p.get("lang","hi")
    return reply_hi(msg, p) if l=="hi" else reply_en(msg, p)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP HANDLER
# ─────────────────────────────────────────────────────────────────────────────

class SaraHandler(BaseHTTPRequestHandler):
    def _json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, payload):
        body = payload.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get("Content-Length","0"))
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._html(HTML_PAGE); return
        if path == "/api/profile":
            self._json({"profile": load_profile()}); return
        if path == "/api/checkin":
            p = load_profile()
            if not p: self._json({"message":None}); return
            self._json({
                "message": dispatch_proactive(p),
                "focus_summary": focus_summary(p),
                "health_summary": health_summary(p),
            }); return
        self._json({"error":"Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/profile":
            p = normalize_profile(self._read_json())
            save_profile(p)
            self._json({
                "profile": p,
                "message": dispatch_welcome(p),
                "focus_summary": focus_summary(p),
                "health_summary": health_summary(p),
            }); return
        if path == "/api/chat":
            p = load_profile()
            if not p:
                self._json({"reply":"Please tell me about yourself first / Pehle apna profile bharo!"}, status=HTTPStatus.BAD_REQUEST); return
            data    = self._read_json()
            msg     = str(data.get("message","")).strip()
            req_lang= str(data.get("lang","")).strip() or p.get("lang","hi")
            if not msg:
                self._json({"reply":"Main sun rahi hoon / I'm listening…"}); return
            # Update mood if personal update
            if any(x in msg.lower() for x in ["i feel","today i","main feel","aaj main","meri health","my health","sleep","neend","stress","energy"]):
                p["mood"] = msg[:160]
                p["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_profile(p)
            self._json({
                "reply": dispatch_reply(msg, p, req_lang),
                "focus_summary": focus_summary(p),
                "health_summary": health_summary(p),
            }); return
        self._json({"error":"Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, *args):
        return


def run():
    server = ThreadingHTTPServer((HOST, PORT), SaraHandler)
    print(f"✨ Sara is ready at http://{HOST}:{PORT}")
    print(f"   Profile stored at: {PROFILE_PATH}")
    print("   Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSara is resting. Bye! 🌸")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()

import json
import random
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "sara_profile.json"
HOST = "127.0.0.1"
PORT = 8010


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Sara — Your Room Companion</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    /* ── TOKENS ─────────────────────────────────────── */
    :root{
      --sage:#3d6b5e;--sage-lt:#6a9e8f;--sage-dk:#243f38;
      --cream:#f5ede0;--parchment:#ede0cf;--warm:#c8956b;
      --blush:#d4788a;--blush-lt:#e8a0b0;--blush-dk:#9d4f60;
      --gold:#d4a843;--gold-lt:#e8c87a;
      --wood-dk:#5c3420;--wood:#7a4830;--wood-lt:#a86040;
      --sky-top:#b8d4e8;--sky-mid:#cde2f0;--sky-bt:#dff0f8;
      --floor:#c8a882;--floor-dk:#a08060;
      --wall-lt:#f0e8d8;--wall-mid:#e8dcc8;
      --text:#2a1f18;--text-mute:#7a6858;
      --radius:20px;--shadow:0 24px 64px rgba(42,31,24,.16);
    }

    /* ── RESET ──────────────────────────────────────── */
    *{box-sizing:border-box;margin:0;padding:0}
    html,body{height:100%;overflow:hidden}
    body{
      font-family:'DM Sans',sans-serif;
      background:linear-gradient(160deg,#2a3f38 0%,#1a2820 100%);
      color:var(--text);
    }

    /* ── LAYOUT ─────────────────────────────────────── */
    .app{
      display:grid;
      grid-template-columns:1fr 400px;
      height:100vh;
      gap:0;
    }

    /* ── LEFT — ROOM ─────────────────────────────────── */
    .room-wrap{
      position:relative;
      overflow:hidden;
      background:linear-gradient(180deg,#1e3530 0%,#2d4840 100%);
    }

    /* ── ROOM SCENE (3-D perspective box) ──────────────── */
    .scene{
      position:absolute;
      inset:0;
      perspective:900px;
      perspective-origin:50% 42%;
    }
    .room-box{
      position:absolute;
      inset:0;
      transform-style:preserve-3d;
    }

    /* ── WALLS ───────────────────────────────────────── */
    .wall{position:absolute;backface-visibility:hidden}

    /* Back wall */
    .wall-back{
      inset:0 0 34% 0;
      background:linear-gradient(180deg,var(--wall-lt) 0%,var(--wall-mid) 100%);
      transform:translateZ(0px);
    }
    /* subtle wallpaper pattern */
    .wall-back::before{
      content:'';position:absolute;inset:0;
      background-image:
        radial-gradient(circle at 20px 20px,rgba(180,150,110,.08) 1px,transparent 1px),
        radial-gradient(circle at 60px 60px,rgba(180,150,110,.06) 1px,transparent 1px);
      background-size:80px 80px;
    }
    /* wainscoting rail */
    .wall-back::after{
      content:'';position:absolute;
      left:0;right:0;bottom:0;height:28%;
      background:linear-gradient(180deg,#e2d4be,#d8c8ae);
      border-top:3px solid rgba(180,150,110,.4);
    }

    /* Left wall */
    .wall-left{
      top:0;bottom:34%;left:0;width:22%;
      background:linear-gradient(90deg,#d0c4b0,#e0d4c0);
      transform-origin:left center;
      transform:rotateY(52deg) translateX(-2px);
    }
    /* Right wall */
    .wall-right{
      top:0;bottom:34%;right:0;width:22%;
      background:linear-gradient(270deg,#d0c4b0,#e0d4c0);
      transform-origin:right center;
      transform:rotateY(-52deg) translateX(2px);
    }

    /* Floor */
    .floor{
      position:absolute;
      left:0;right:0;bottom:0;height:36%;
      background:linear-gradient(180deg,var(--floor) 0%,var(--floor-dk) 100%);
      transform-origin:bottom center;
      transform:rotateX(40deg) translateY(10px);
    }
    /* floor planks */
    .floor::before{
      content:'';position:absolute;inset:0;
      background:repeating-linear-gradient(
        90deg,
        transparent 0px,
        transparent 119px,
        rgba(0,0,0,.06) 119px,
        rgba(0,0,0,.06) 120px
      );
    }
    .floor::after{
      content:'';position:absolute;inset:0;
      background:repeating-linear-gradient(
        180deg,
        transparent 0px,
        transparent 29px,
        rgba(0,0,0,.04) 29px,
        rgba(0,0,0,.04) 30px
      );
    }

    /* ── WINDOW ──────────────────────────────────────── */
    .window-frame{
      position:absolute;
      top:6%;left:50%;
      width:28%;
      aspect-ratio:4/5;
      transform:translateX(-50%);
      background:#fff;
      border:14px solid #c8a87a;
      border-radius:8px 8px 4px 4px;
      box-shadow:
        inset 0 0 0 3px rgba(255,255,255,.5),
        0 8px 32px rgba(42,31,24,.2),
        0 2px 8px rgba(42,31,24,.1);
      overflow:hidden;
      z-index:2;
    }
    .window-sky{
      position:absolute;inset:0;
      background:linear-gradient(180deg,var(--sky-top),var(--sky-mid),var(--sky-bt));
      overflow:hidden;
    }
    /* clouds */
    .cloud{
      position:absolute;
      background:#fff;
      border-radius:50px;
      opacity:.85;
      animation:drift linear infinite;
    }
    .cloud::before,.cloud::after{
      content:'';position:absolute;
      background:#fff;border-radius:50%;
    }
    .cloud.c1{width:70px;height:22px;top:18%;left:-80px;animation-duration:18s;animation-delay:0s}
    .cloud.c1::before{width:38px;height:32px;top:-16px;left:10px}
    .cloud.c1::after{width:28px;height:24px;top:-12px;left:32px}
    .cloud.c2{width:50px;height:16px;top:38%;left:-60px;animation-duration:24s;animation-delay:6s;opacity:.7}
    .cloud.c2::before{width:28px;height:22px;top:-12px;left:8px}
    .cloud.c3{width:60px;height:18px;top:58%;left:-70px;animation-duration:20s;animation-delay:3s;opacity:.6}
    .cloud.c3::before{width:32px;height:28px;top:-14px;left:10px}
    @keyframes drift{to{transform:translateX(calc(100vw + 100px))}}

    /* Hills outside */
    .hill{position:absolute;border-radius:50% 50% 0 0}
    .hill1{width:120%;height:48%;bottom:0;left:-10%;background:linear-gradient(180deg,#7aaa88,#5a8a68)}
    .hill2{width:80%;height:36%;bottom:0;left:10%;background:linear-gradient(180deg,#6a9a78,#4a7a58)}
    .hill3{width:60%;height:28%;bottom:0;right:0;background:linear-gradient(180deg,#88b094,#68906e)}
    /* tiny tree */
    .tree{position:absolute;bottom:28%}
    .tree-trunk{width:6px;height:20px;background:#5c3c1e;border-radius:2px;margin:0 auto}
    .tree-top{width:0;height:0;border-left:14px solid transparent;border-right:14px solid transparent;border-bottom:28px solid #3a6e48;margin:0 auto;margin-top:-4px}
    .tree1{left:18%}.tree2{left:34%;bottom:32%}.tree3{right:14%}

    /* Window dividers */
    .win-cross-h{position:absolute;top:50%;left:0;right:0;height:5px;background:#c8a87a;transform:translateY(-50%);z-index:2}
    .win-cross-v{position:absolute;left:50%;top:0;bottom:0;width:5px;background:#c8a87a;transform:translateX(-50%);z-index:2}

    /* Curtains */
    .curtain{
      position:absolute;top:-14px;bottom:-14px;width:38%;
      border-radius:0 0 8px 8px;
      z-index:3;
      overflow:hidden;
    }
    .curtain::before,.curtain::after{
      content:'';position:absolute;
      top:0;bottom:0;width:50%;
      background:inherit;
      clip-path:polygon(0 0,100% 0,85% 100%,15% 100%);
    }
    .curtain-l{
      left:-14px;
      background:linear-gradient(90deg,#c05070,#e07090);
      clip-path:polygon(0 0,100% 0,80% 100%,0 100%);
    }
    .curtain-r{
      right:-14px;
      background:linear-gradient(270deg,#c05070,#e07090);
      clip-path:polygon(0 0,100% 0,100% 100%,20% 100%);
    }
    /* curtain valance */
    .valance{
      position:absolute;top:-14px;left:-14px;right:-14px;height:24px;
      background:linear-gradient(90deg,#b04060,#e07090,#b04060);
      border-radius:4px;
      z-index:4;
      box-shadow:0 4px 8px rgba(0,0,0,.2);
    }

    /* ── BOOKSHELF ────────────────────────────────────── */
    .bookshelf{
      position:absolute;
      right:6%;top:8%;
      width:18%;
      z-index:3;
    }
    .shelf-unit{
      background:linear-gradient(180deg,var(--wood) 0%,var(--wood-dk) 100%);
      border-radius:10px 10px 4px 4px;
      padding:8px;
      box-shadow:
        4px 8px 24px rgba(42,31,24,.35),
        inset -2px 0 6px rgba(0,0,0,.2);
    }
    .shelf-row{
      display:flex;
      align-items:flex-end;
      gap:3px;
      padding:6px 4px 4px;
      background:var(--wood-lt);
      border-radius:4px;
      margin-bottom:6px;
      position:relative;
    }
    .shelf-row::after{
      content:'';position:absolute;
      left:0;right:0;bottom:0;height:5px;
      background:rgba(0,0,0,.2);
      border-radius:0 0 4px 4px;
    }
    .shelf-row:last-child{margin-bottom:0}
    .book{
      border-radius:2px 2px 0 0;
      flex-shrink:0;
    }
    /* row 1 */
    .bk1{width:13px;height:44px;background:linear-gradient(180deg,#5a8f6a,#3a6f4a)}
    .bk2{width:10px;height:52px;background:linear-gradient(180deg,#d4943a,#b4741a)}
    .bk3{width:14px;height:38px;background:linear-gradient(180deg,#b05878,#904058)}
    .bk4{width:9px;height:48px;background:linear-gradient(180deg,#5878b0,#385890)}
    .bk5{width:12px;height:42px;background:linear-gradient(180deg,#d4c43a,#b4a41a)}
    /* row 2 */
    .bk6{width:14px;height:46px;background:linear-gradient(180deg,#78b08a,#489a5a)}
    .bk7{width:11px;height:50px;background:linear-gradient(180deg,#e07858,#c05838)}
    .bk8{width:13px;height:40px;background:linear-gradient(180deg,#9058b0,#703890)}
    .bk9{width:10px;height:54px;background:linear-gradient(180deg,#4890c8,#2870a8)}
    .bk10{width:12px;height:36px;background:linear-gradient(180deg,#e0a858,#c08838)}
    /* row 3 */
    .bk11{width:16px;height:48px;background:linear-gradient(180deg,#c87888,#a85868)}
    .bk12{width:10px;height:42px;background:linear-gradient(180deg,#78c8a8,#489888)}
    .bk13{width:13px;height:56px;background:linear-gradient(180deg,#f0d068,#d0b048)}
    .bk14{width:11px;height:38px;background:linear-gradient(180deg,#8898d0,#6878b0)}
    /* small decor on shelf */
    .shelf-plant{width:18px;height:22px;background:linear-gradient(180deg,#5a9068,#3a7048);border-radius:50% 50% 4px 4px;margin-bottom:2px}
    .shelf-deco{width:12px;height:16px;background:linear-gradient(180deg,#d4843a,#b46420);border-radius:50% 50% 4px 4px;margin-bottom:2px}

    /* ── DESK ────────────────────────────────────────── */
    .desk-wrap{
      position:absolute;
      left:50%;bottom:36%;
      transform:translateX(-50%);
      width:56%;
      z-index:4;
    }
    .desk-surface{
      background:linear-gradient(180deg,var(--wood-lt),var(--wood));
      border-radius:10px 10px 0 0;
      height:18px;
      box-shadow:0 -2px 8px rgba(0,0,0,.15);
    }
    .desk-body{
      background:linear-gradient(180deg,var(--wood),var(--wood-dk));
      height:14px;
      border-radius:0 0 6px 6px;
    }
    .desk-legs{
      display:flex;
      justify-content:space-between;
      padding:0 8px;
    }
    .desk-leg{
      width:8px;height:42px;
      background:linear-gradient(180deg,var(--wood-dk),#3c2010);
      border-radius:0 0 4px 4px;
    }

    /* Desk items */
    .desk-items{
      position:absolute;
      bottom:18px;left:0;right:0;
      display:flex;
      align-items:flex-end;
      gap:0;
      padding:0 10px;
    }

    /* Laptop */
    .laptop-wrap{
      position:relative;
      margin-left:10px;
    }
    .laptop-screen{
      width:62px;height:40px;
      background:linear-gradient(135deg,#1a2535,#243548);
      border-radius:4px 4px 0 0;
      border:3px solid #3a4555;
      position:relative;
      transform-origin:bottom center;
      transform:rotateX(-15deg);
      overflow:hidden;
    }
    .laptop-screen::before{
      content:'';position:absolute;inset:4px;
      background:linear-gradient(135deg,#0f3048,#1a4058);
      border-radius:2px;
    }
    /* screen glow lines */
    .laptop-screen::after{
      content:'';position:absolute;
      left:6px;top:8px;right:6px;
      height:2px;background:rgba(100,200,255,.3);
      box-shadow:0 5px 0 rgba(100,200,255,.2),0 10px 0 rgba(100,200,255,.15),0 15px 0 rgba(100,200,255,.1);
    }
    .laptop-base{
      width:66px;height:5px;
      background:linear-gradient(180deg,#b0b8c0,#8090a0);
      border-radius:0 0 4px 4px;
    }

    /* Tea mug */
    .mug-wrap{position:relative;margin-left:8px}
    .mug{
      width:22px;height:26px;
      background:linear-gradient(180deg,#f0ebe0,#e0d5c0);
      border-radius:4px 4px 6px 6px;
      position:relative;
      box-shadow:inset -2px 0 4px rgba(0,0,0,.1);
    }
    .mug::before{/* tea inside */
      content:'';position:absolute;
      top:5px;left:3px;right:3px;height:6px;
      background:linear-gradient(180deg,#c8783a,#b06028);
      border-radius:2px;
    }
    .mug-handle{
      position:absolute;
      right:-8px;top:6px;
      width:8px;height:12px;
      border:3px solid #e0d5c0;
      border-left:none;
      border-radius:0 6px 6px 0;
    }
    .steam{
      position:absolute;
      bottom:26px;
      display:flex;gap:4px;
    }
    .steam-line{
      width:2px;
      background:linear-gradient(180deg,transparent,rgba(255,255,255,.6));
      border-radius:1px;
      animation:steam-rise 2s ease-in-out infinite;
    }
    .steam-line:nth-child(1){height:12px;animation-delay:0s}
    .steam-line:nth-child(2){height:16px;animation-delay:.4s}
    .steam-line:nth-child(3){height:10px;animation-delay:.8s}
    @keyframes steam-rise{
      0%,100%{opacity:0;transform:translateY(0) scaleX(1)}
      40%{opacity:.8;transform:translateY(-8px) scaleX(1.5)}
      80%{opacity:0;transform:translateY(-16px) scaleX(.5)}
    }

    /* Desk plant */
    .desk-plant{
      position:relative;
      margin-left:auto;
      margin-right:6px;
    }
    .pot{
      width:24px;height:18px;
      background:linear-gradient(180deg,#c87848,#a85828);
      border-radius:2px 2px 6px 6px;
      clip-path:polygon(5% 0,95% 0,100% 100%,0 100%);
    }
    .plant-stem{
      width:3px;height:28px;
      background:linear-gradient(180deg,#4a8a58,#2a6a38);
      margin:0 auto;
      margin-top:-2px;
      border-radius:2px;
    }
    .plant-leaf{
      position:absolute;
      background:linear-gradient(135deg,#5a9a68,#3a7a48);
      border-radius:50%;
    }
    .leaf1{width:20px;height:12px;top:4px;left:-14px;transform:rotate(-30deg)}
    .leaf2{width:18px;height:11px;top:8px;right:-12px;transform:rotate(25deg)}
    .leaf3{width:16px;height:10px;top:12px;left:-10px;transform:rotate(-45deg)}
    .leaf4{width:14px;height:9px;top:0;left:2px;transform:rotate(10deg)}

    /* Desk lamp */
    .lamp-wrap{
      position:absolute;
      left:10px;bottom:18px;
      z-index:5;
    }
    .lamp-base{
      width:20px;height:6px;
      background:linear-gradient(180deg,#8890a0,#6878 90);
      border-radius:10px;
    }
    .lamp-arm1{
      width:4px;height:30px;
      background:linear-gradient(180deg,#9898a8,#7878 90);
      margin:0 auto;
      border-radius:2px;
      transform:rotate(-10deg);
      transform-origin:bottom center;
    }
    .lamp-arm2{
      width:4px;height:24px;
      background:linear-gradient(180deg,#9898a8,#7878 90);
      margin:0 auto;
      border-radius:2px;
      transform:rotate(20deg);
      transform-origin:bottom left;
    }
    .lamp-head{
      width:32px;height:16px;
      background:linear-gradient(180deg,#f0d060,#d0a830);
      border-radius:50% 50% 8px 8px;
      margin-left:-12px;
      box-shadow:0 8px 24px rgba(240,200,60,.4);
    }
    /* lamp glow on desk */
    .lamp-glow{
      position:absolute;
      bottom:0;left:-10px;
      width:80px;height:20px;
      background:radial-gradient(ellipse,rgba(240,200,60,.25),transparent 70%);
      border-radius:50%;
      pointer-events:none;
    }

    /* ── FLOOR RUG ────────────────────────────────────── */
    .rug{
      position:absolute;
      left:50%;bottom:35%;
      transform:translateX(-50%) rotateX(40deg);
      width:50%;height:60px;
      background:linear-gradient(90deg,#8a4a6a,#b86a8a,#d48aaa,#b86a8a,#8a4a6a);
      border-radius:8px;
      z-index:3;
      box-shadow:0 8px 16px rgba(0,0,0,.2);
    }
    .rug::before{
      content:'';position:absolute;
      inset:6px;
      border:2px solid rgba(255,255,255,.2);
      border-radius:4px;
    }

    /* ── SARA AVATAR ──────────────────────────────────── */
    .avatar-wrap{
      position:absolute;
      left:50%;bottom:35%;
      transform:translateX(-50%);
      z-index:10;
      animation:float 5s ease-in-out infinite;
    }
    @keyframes float{
      0%,100%{transform:translateX(-50%) translateY(0)}
      50%{transform:translateX(-50%) translateY(-10px)}
    }
    .avatar-shadow{
      position:absolute;
      bottom:-6px;left:50%;
      transform:translateX(-50%);
      width:90px;height:16px;
      background:radial-gradient(ellipse,rgba(42,31,24,.35),transparent 70%);
      border-radius:50%;
    }

    /* SVG avatar sizing */
    .avatar-svg{
      width:160px;
      filter:drop-shadow(0 16px 32px rgba(42,31,24,.3));
    }

    /* ── SPEECH BUBBLE ────────────────────────────────── */
    .speech-bubble{
      position:absolute;
      left:calc(50% + 90px);
      bottom:calc(35% + 180px);
      max-width:220px;
      background:rgba(255,252,245,.96);
      border:1px solid rgba(180,150,110,.2);
      border-radius:20px 20px 20px 4px;
      padding:14px 16px;
      font-size:.82rem;
      line-height:1.6;
      color:var(--text);
      box-shadow:0 16px 40px rgba(42,31,24,.15);
      z-index:11;
      animation:bubblePop .4s cubic-bezier(.34,1.56,.64,1);
      backdrop-filter:blur(8px);
    }
    @keyframes bubblePop{
      from{opacity:0;transform:scale(.8) translateY(10px)}
      to{opacity:1;transform:scale(1) translateY(0)}
    }

    /* ── FRAME OVERLAY (room depth vignette) ─────────── */
    .room-vignette{
      position:absolute;inset:0;
      background:radial-gradient(ellipse at 50% 40%,transparent 40%,rgba(20,30,26,.45) 100%);
      pointer-events:none;
      z-index:20;
    }
    .room-frame{
      position:absolute;inset:0;
      border:22px solid rgba(20,16,12,.5);
      border-radius:0;
      pointer-events:none;
      z-index:21;
      box-shadow:inset 0 0 60px rgba(0,0,0,.3);
    }

    /* ── TIME / GREETING BAR ─────────────────────────── */
    .room-header{
      position:absolute;
      top:18px;left:18px;right:18px;
      display:flex;
      justify-content:space-between;
      align-items:center;
      z-index:22;
    }
    .room-badge{
      background:rgba(20,30,26,.7);
      color:#e8d8c0;
      padding:8px 16px;
      border-radius:999px;
      font-size:.78rem;
      font-weight:600;
      letter-spacing:.05em;
      backdrop-filter:blur(12px);
      border:1px solid rgba(255,255,255,.08);
    }
    .time-display{
      background:rgba(20,30,26,.7);
      color:#e8d8c0;
      padding:8px 16px;
      border-radius:999px;
      font-size:.82rem;
      font-family:'Playfair Display',serif;
      backdrop-filter:blur(12px);
      border:1px solid rgba(255,255,255,.08);
    }

    /* ── RIGHT PANEL ─────────────────────────────────── */
    .panel-right{
      display:flex;
      flex-direction:column;
      background:linear-gradient(160deg,#f8f2e8 0%,#f0e8d8 100%);
      border-left:1px solid rgba(180,150,110,.2);
      overflow:hidden;
    }

    .panel-head{
      padding:20px 22px 14px;
      border-bottom:1px solid rgba(180,150,110,.15);
      background:rgba(255,252,246,.8);
      backdrop-filter:blur(8px);
    }
    .panel-title{
      font-family:'Playfair Display',serif;
      font-size:1.4rem;
      color:var(--sage-dk);
      line-height:1;
    }
    .panel-sub{
      font-size:.78rem;
      color:var(--text-mute);
      margin-top:4px;
    }

    /* ── STATUS PILLS ─────────────────────────────────── */
    .status-row{
      display:flex;gap:8px;
      padding:10px 22px;
      flex-wrap:wrap;
      border-bottom:1px solid rgba(180,150,110,.1);
    }
    .status-pill{
      padding:5px 12px;
      border-radius:999px;
      font-size:.72rem;
      font-weight:600;
      letter-spacing:.04em;
    }
    .pill-green{background:rgba(61,107,94,.12);color:var(--sage-dk)}
    .pill-rose{background:rgba(180,80,100,.12);color:var(--blush-dk)}
    .pill-gold{background:rgba(180,140,50,.12);color:#8a6010}

    /* ── CHECK-IN BANNER ─────────────────────────────── */
    .checkin-banner{
      margin:12px 22px 0;
      background:linear-gradient(135deg,var(--sage-dk),var(--sage));
      border-radius:16px;
      padding:14px 16px;
      color:#fff;
    }
    .checkin-banner strong{font-size:.85rem;letter-spacing:.03em}
    .checkin-text{font-size:.78rem;margin-top:4px;opacity:.9;line-height:1.5}
    .mood-row{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
    .mood-btn{
      padding:6px 14px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.3);
      background:rgba(255,255,255,.15);
      color:#fff;
      font:600 .75rem 'DM Sans',sans-serif;
      cursor:pointer;
      transition:all .2s;
    }
    .mood-btn:hover{background:rgba(255,255,255,.28)}

    /* ── PROFILE / CHAT AREA ─────────────────────────── */
    .content-area{
      flex:1;
      overflow-y:auto;
      padding:12px 22px 0;
    }
    .content-area::-webkit-scrollbar{width:4px}
    .content-area::-webkit-scrollbar-track{background:transparent}
    .content-area::-webkit-scrollbar-thumb{background:rgba(180,150,110,.3);border-radius:2px}

    /* Profile form */
    .profile-intro{
      font-size:.82rem;
      color:var(--text-mute);
      line-height:1.6;
      margin-bottom:14px;
      padding:12px 14px;
      background:rgba(255,252,246,.8);
      border-radius:12px;
      border:1px solid rgba(180,150,110,.15);
    }
    .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
    .form-full{grid-column:1/-1}
    .form-label{
      display:block;
      font-size:.72rem;
      font-weight:600;
      color:var(--sage-dk);
      letter-spacing:.04em;
      margin-bottom:5px;
    }
    .form-input,.form-textarea{
      width:100%;
      font:400 .82rem 'DM Sans',sans-serif;
      background:#fff;
      border:1.5px solid rgba(180,150,110,.2);
      border-radius:10px;
      padding:10px 12px;
      color:var(--text);
      transition:border-color .2s;
      outline:none;
    }
    .form-input:focus,.form-textarea:focus{border-color:var(--sage);box-shadow:0 0 0 3px rgba(61,107,94,.08)}
    .form-textarea{resize:vertical;min-height:68px}
    .btn-primary{
      width:100%;
      padding:12px;
      background:linear-gradient(135deg,var(--sage-dk),var(--sage));
      color:#fff;
      border:none;
      border-radius:12px;
      font:700 .88rem 'DM Sans',sans-serif;
      cursor:pointer;
      transition:opacity .2s,transform .1s;
      margin-top:4px;
    }
    .btn-primary:hover{opacity:.9}
    .btn-primary:active{transform:scale(.98)}

    /* Chat */
    .chat-log{
      display:flex;
      flex-direction:column;
      gap:10px;
      padding-bottom:12px;
    }
    .bubble{
      max-width:85%;
      padding:12px 14px;
      border-radius:16px;
      font-size:.82rem;
      line-height:1.6;
      white-space:pre-wrap;
    }
    .bubble-sara{
      background:#fff;
      border:1px solid rgba(180,150,110,.15);
      border-radius:4px 16px 16px 16px;
      align-self:flex-start;
      box-shadow:0 4px 12px rgba(42,31,24,.06);
    }
    .bubble-user{
      background:linear-gradient(135deg,var(--sage-dk),var(--sage));
      color:#fff;
      border-radius:16px 4px 16px 16px;
      align-self:flex-end;
    }

    /* Quick tools */
    .tool-row{
      display:flex;gap:8px;flex-wrap:wrap;
      padding:10px 22px;
      border-top:1px solid rgba(180,150,110,.1);
      background:rgba(255,252,246,.8);
    }
    .tool-btn{
      padding:7px 14px;
      border-radius:999px;
      border:1.5px solid rgba(61,107,94,.25);
      background:#fff;
      color:var(--sage-dk);
      font:600 .75rem 'DM Sans',sans-serif;
      cursor:pointer;
      transition:all .2s;
    }
    .tool-btn:hover{background:var(--sage-dk);color:#fff;border-color:var(--sage-dk)}

    /* Compose */
    .compose-area{
      padding:12px 22px 16px;
      border-top:1px solid rgba(180,150,110,.12);
      background:rgba(255,252,246,.9);
      display:grid;
      grid-template-columns:1fr auto auto;
      gap:8px;
      align-items:end;
    }
    .compose-input{
      font:400 .84rem 'DM Sans',sans-serif;
      background:#fff;
      border:1.5px solid rgba(180,150,110,.2);
      border-radius:12px;
      padding:10px 14px;
      resize:none;
      min-height:44px;
      max-height:120px;
      outline:none;
      color:var(--text);
      transition:border-color .2s;
    }
    .compose-input:focus{border-color:var(--sage)}
    .btn-icon{
      width:44px;height:44px;
      border-radius:12px;
      border:1.5px solid rgba(180,150,110,.2);
      background:#fff;
      cursor:pointer;
      display:grid;place-items:center;
      font-size:1.1rem;
      transition:all .2s;
    }
    .btn-icon:hover{background:var(--sage-dk);border-color:var(--sage-dk);color:#fff}
    .btn-send{
      width:44px;height:44px;
      border-radius:12px;
      border:none;
      background:linear-gradient(135deg,var(--sage-dk),var(--sage));
      color:#fff;
      cursor:pointer;
      display:grid;place-items:center;
      font-size:1.1rem;
      transition:opacity .2s,transform .1s;
    }
    .btn-send:hover{opacity:.88}
    .btn-send:active{transform:scale(.94)}

    /* Sidebar cards */
    .side-cards{
      display:grid;
      gap:8px;
      padding-bottom:12px;
    }
    .side-card{
      background:#fff;
      border:1px solid rgba(180,150,110,.15);
      border-radius:14px;
      padding:12px 14px;
      box-shadow:0 2px 8px rgba(42,31,24,.04);
    }
    .side-card-title{
      font-size:.7rem;
      font-weight:700;
      color:var(--sage-dk);
      letter-spacing:.06em;
      text-transform:uppercase;
      margin-bottom:6px;
    }
    .side-card-body{font-size:.78rem;color:var(--text-mute);line-height:1.5}

    /* Voice line */
    .voice-line{
      text-align:center;
      font-size:.72rem;
      color:var(--text-mute);
      padding:8px;
    }

    /* Utils */
    .hide{display:none!important}

    /* Animations for room elements */
    @keyframes sway{
      0%,100%{transform:rotate(-2deg)}
      50%{transform:rotate(2deg)}
    }

    /* Responsive */
    @media(max-width:900px){
      .app{grid-template-columns:1fr;height:auto;overflow:auto}
      html,body{overflow:auto;height:auto}
      .room-wrap{height:60vw;min-height:360px}
      .panel-right{height:auto}
    }
  </style>
</head>
<body>
<div class="app">

  <!-- ══ LEFT: 3D ROOM ══ -->
  <div class="room-wrap">
    <div class="scene">
      <div class="room-box">

        <!-- Walls -->
        <div class="wall wall-back"></div>
        <div class="wall wall-left"></div>
        <div class="wall wall-right"></div>
        <div class="floor"></div>

        <!-- Window -->
        <div class="window-frame" style="position:absolute;top:7%;left:50%;transform:translateX(-50%);width:26%;z-index:2">
          <div class="window-sky">
            <div class="hill hill1"></div>
            <div class="hill hill2"></div>
            <div class="hill hill3"></div>
            <div class="tree tree1"><div class="tree-trunk"></div><div class="tree-top"></div></div>
            <div class="tree tree2"><div class="tree-trunk"></div><div class="tree-top"></div></div>
            <div class="tree tree3"><div class="tree-trunk"></div><div class="tree-top"></div></div>
            <div class="cloud c1"></div>
            <div class="cloud c2"></div>
            <div class="cloud c3"></div>
          </div>
          <div class="win-cross-h"></div>
          <div class="win-cross-v"></div>
          <div class="curtain curtain-l"></div>
          <div class="curtain curtain-r"></div>
          <div class="valance"></div>
        </div>

        <!-- Bookshelf -->
        <div class="bookshelf">
          <div class="shelf-unit">
            <div class="shelf-row">
              <div class="book bk1"></div>
              <div class="book bk2"></div>
              <div class="book bk3"></div>
              <div class="book bk4"></div>
              <div class="book bk5"></div>
              <div class="shelf-deco"></div>
            </div>
            <div class="shelf-row">
              <div class="shelf-plant"></div>
              <div class="book bk6"></div>
              <div class="book bk7"></div>
              <div class="book bk8"></div>
              <div class="book bk9"></div>
              <div class="book bk10"></div>
            </div>
            <div class="shelf-row">
              <div class="book bk11"></div>
              <div class="book bk12"></div>
              <div class="book bk13"></div>
              <div class="book bk14"></div>
            </div>
          </div>
        </div>

        <!-- Rug -->
        <div class="rug"></div>

        <!-- Desk -->
        <div class="desk-wrap">
          <!-- Lamp (behind desk items) -->
          <div class="lamp-wrap" style="position:absolute;left:8px;bottom:18px;z-index:5">
            <div class="lamp-base"></div>
            <div class="lamp-arm1"></div>
            <div class="lamp-arm2" style="margin-left:4px"></div>
            <div class="lamp-head"></div>
            <div class="lamp-glow"></div>
          </div>
          <!-- Desk items -->
          <div class="desk-items">
            <div style="width:50px"></div><!-- lamp spacer -->
            <div class="laptop-wrap">
              <div class="laptop-screen"></div>
              <div class="laptop-base"></div>
            </div>
            <div class="mug-wrap">
              <div class="steam">
                <div class="steam-line"></div>
                <div class="steam-line"></div>
                <div class="steam-line"></div>
              </div>
              <div class="mug"><div class="mug-handle"></div></div>
            </div>
            <div class="desk-plant">
              <div style="position:relative">
                <div class="plant-leaf leaf1"></div>
                <div class="plant-leaf leaf2"></div>
                <div class="plant-leaf leaf3"></div>
                <div class="plant-leaf leaf4"></div>
                <div class="plant-stem"></div>
              </div>
              <div class="pot"></div>
            </div>
          </div>
          <div class="desk-surface"></div>
          <div class="desk-body"></div>
          <div class="desk-legs">
            <div class="desk-leg"></div>
            <div class="desk-leg"></div>
          </div>
        </div>

        <!-- Sara Avatar -->
        <div class="avatar-wrap">
          <div class="avatar-shadow"></div>
          <svg class="avatar-svg" viewBox="0 0 160 320" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Hair back -->
            <ellipse cx="80" cy="68" rx="46" ry="52" fill="#2d1e14"/>
            <!-- Body dress -->
            <path d="M42 148 Q40 220 38 280 Q60 290 80 290 Q100 290 122 280 Q120 220 118 148 Q100 160 80 160 Q60 160 42 148Z" fill="#c05878"/>
            <path d="M42 148 Q40 220 38 280 Q60 290 80 290 Q100 290 122 280 Q120 220 118 148 Q100 160 80 160 Q60 160 42 148Z" fill="url(#dressGrad)"/>
            <!-- Dress highlight -->
            <path d="M55 152 Q54 180 53 210" stroke="rgba(255,255,255,.15)" stroke-width="8" stroke-linecap="round"/>
            <!-- Skirt flare -->
            <path d="M36 240 Q30 280 28 300 Q54 310 80 310 Q106 310 132 300 Q130 280 124 240Z" fill="#a04068"/>
            <path d="M36 240 Q30 280 28 300 Q54 310 80 310 Q106 310 132 300 Q130 280 124 240Z" fill="url(#skirtGrad)"/>
            <!-- Left arm -->
            <path d="M42 148 Q22 180 20 210 Q26 212 34 208 Q38 180 52 158Z" fill="#ffd0b0"/>
            <!-- Right arm (waving) -->
            <path d="M118 148 Q142 170 150 195 Q144 200 138 196 Q130 174 108 158Z" fill="#ffd0b0" style="transform-origin:118px 158px;animation:waveArm 3s ease-in-out infinite"/>
            <!-- Hand right -->
            <ellipse cx="144" cy="198" rx="9" ry="7" fill="#ffd0b0" style="transform-origin:118px 158px;animation:waveArm 3s ease-in-out infinite"/>
            <!-- Hand left -->
            <ellipse cx="22" cy="210" rx="8" ry="7" fill="#ffd0b0"/>
            <!-- Collar -->
            <path d="M62 148 Q80 156 98 148 L94 140 Q80 148 66 140Z" fill="#e07898"/>
            <!-- Neck -->
            <rect x="73" y="108" width="14" height="22" rx="7" fill="#ffd0b0"/>
            <!-- Head -->
            <ellipse cx="80" cy="84" rx="40" ry="44" fill="#ffd0b0"/>
            <!-- Hair front -->
            <path d="M40 72 Q40 36 80 30 Q120 36 120 72 Q110 54 80 52 Q50 54 40 72Z" fill="#2d1e14"/>
            <!-- Hair side left -->
            <path d="M40 72 Q34 90 36 112 Q42 106 44 90 Q42 80 40 72Z" fill="#2d1e14"/>
            <!-- Hair side right -->
            <path d="M120 72 Q126 90 124 112 Q118 106 116 90 Q118 80 120 72Z" fill="#2d1e14"/>
            <!-- Hair bun -->
            <circle cx="80" cy="34" r="14" fill="#2d1e14"/>
            <circle cx="80" cy="34" r="10" fill="#3d2820"/>
            <!-- Eyes -->
            <ellipse cx="64" cy="88" rx="7" ry="7.5" fill="#fff"/>
            <ellipse cx="96" cy="88" rx="7" ry="7.5" fill="#fff"/>
            <circle cx="65" cy="89" r="4.5" fill="#2d1e14"/>
            <circle cx="97" cy="89" r="4.5" fill="#2d1e14"/>
            <!-- Eye shine -->
            <circle cx="67" cy="87" r="1.5" fill="#fff"/>
            <circle cx="99" cy="87" r="1.5" fill="#fff"/>
            <!-- Eyelashes -->
            <path d="M57 83 Q60 79 64 83" stroke="#2d1e14" stroke-width="1.5" stroke-linecap="round" fill="none"/>
            <path d="M89 83 Q93 79 97 83" stroke="#2d1e14" stroke-width="1.5" stroke-linecap="round" fill="none"/>
            <!-- Brows -->
            <path d="M56 79 Q64 75 72 78" stroke="#4d2e1e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <path d="M88 78 Q96 75 104 79" stroke="#4d2e1e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <!-- Nose -->
            <path d="M77 100 Q80 106 83 100" stroke="#d4a080" stroke-width="1.5" stroke-linecap="round" fill="none"/>
            <!-- Smile -->
            <path d="M68 112 Q80 122 92 112" stroke="#c07858" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <!-- Cheek blush -->
            <ellipse cx="55" cy="102" rx="10" ry="6" fill="rgba(220,120,120,.25)"/>
            <ellipse cx="105" cy="102" rx="10" ry="6" fill="rgba(220,120,120,.25)"/>
            <!-- Earrings -->
            <circle cx="40" cy="98" r="4" fill="#d4a843"/>
            <circle cx="120" cy="98" r="4" fill="#d4a843"/>
            <!-- Legs -->
            <rect x="64" y="296" width="18" height="60" rx="9" fill="#ffd0b0"/>
            <rect x="84" y="296" width="18" height="60" rx="9" fill="#ffd0b0"/>
            <!-- Shoes -->
            <ellipse cx="73" cy="354" rx="13" ry="7" fill="#2d1e14"/>
            <ellipse cx="93" cy="354" rx="13" ry="7" fill="#2d1e14"/>
            <!-- Dress bow -->
            <path d="M70 148 Q80 142 90 148" stroke="#e898b0" stroke-width="3" stroke-linecap="round" fill="none"/>
            <circle cx="80" cy="146" r="3" fill="#e898b0"/>
            <defs>
              <linearGradient id="dressGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="rgba(255,255,255,.1)"/>
                <stop offset="100%" stop-color="rgba(0,0,0,.05)"/>
              </linearGradient>
              <linearGradient id="skirtGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="rgba(255,255,255,.05)"/>
                <stop offset="100%" stop-color="rgba(0,0,0,.15)"/>
              </linearGradient>
            </defs>
          </svg>
        </div>

        <!-- Speech bubble -->
        <div class="speech-bubble" id="speechBubble">Hi friend, how is your health and how is today going? ✨</div>

      </div><!-- room-box -->
    </div><!-- scene -->

    <!-- Room overlays -->
    <div class="room-vignette"></div>
    <div class="room-frame"></div>

    <!-- Header bar -->
    <div class="room-header">
      <div class="room-badge">🌿 Sara's Room</div>
      <div class="time-display" id="clockDisplay">—</div>
    </div>

  </div><!-- room-wrap -->

  <!-- ══ RIGHT: PANEL ══ -->
  <div class="panel-right">

    <div class="panel-head">
      <div class="panel-title">Sara</div>
      <div class="panel-sub" id="statusSub">Waiting to know you</div>
    </div>

    <div class="status-row">
      <div class="status-pill pill-green" id="modePill">Room mode</div>
      <div class="status-pill pill-rose" id="moodPill">Mood: —</div>
      <div class="status-pill pill-gold" id="healthPill">Health: —</div>
    </div>

    <div class="checkin-banner">
      <strong>Daily check-in</strong>
      <div class="checkin-text" id="dailyPromptText">Sara will ask about sleep, energy, food, water, stress, and what is going on today.</div>
      <div class="mood-row">
        <button class="mood-btn" data-checkin="I feel energetic and clear today.">💪 Strong</button>
        <button class="mood-btn" data-checkin="I feel okay but a little stressed and tired today.">😐 Mixed</button>
        <button class="mood-btn" data-checkin="I feel low on energy and I want gentle support today.">🫶 Need care</button>
      </div>
    </div>

    <!-- Scrollable content -->
    <div class="content-area" id="contentArea">

      <!-- Profile form -->
      <div id="profileSection" style="padding-top:12px">
        <div class="profile-intro">Tell Sara about yourself first. She will speak, check on your health, and support your day more personally.</div>
        <form id="profileForm" class="form-grid">
          <div>
            <label class="form-label" for="name">Your name</label>
            <input class="form-input" id="name" name="name" required placeholder="What should Sara call you?">
          </div>
          <div>
            <label class="form-label" for="city">City / Country</label>
            <input class="form-input" id="city" name="city" placeholder="Where are you from?">
          </div>
          <div>
            <label class="form-label" for="age">Age / Life stage</label>
            <input class="form-input" id="age" name="age" placeholder="Student, working…">
          </div>
          <div>
            <label class="form-label" for="mood">Current mood</label>
            <input class="form-input" id="mood" name="mood" placeholder="Calm, tired, excited…">
          </div>
          <div>
            <label class="form-label" for="health">Health & energy</label>
            <input class="form-input" id="health" name="health" placeholder="Sleep, body, energy…">
          </div>
          <div>
            <label class="form-label" for="today">What's going on today</label>
            <input class="form-input" id="today" name="today" placeholder="Class, work, rest…">
          </div>
          <div class="form-full">
            <label class="form-label" for="interests">Interests</label>
            <textarea class="form-textarea" id="interests" name="interests" placeholder="Coding, music, art, fitness, study…"></textarea>
          </div>
          <div class="form-full">
            <label class="form-label" for="goals">Goals</label>
            <textarea class="form-textarea" id="goals" name="goals" placeholder="What do you want Sara to help you with?"></textarea>
          </div>
          <div class="form-full">
            <label class="form-label" for="routine">Routine</label>
            <textarea class="form-textarea" id="routine" name="routine" placeholder="How your day usually goes."></textarea>
          </div>
          <div class="form-full">
            <button class="btn-primary" type="submit">Save profile & wake Sara ✨</button>
          </div>
        </form>
      </div>

      <!-- Chat section -->
      <div id="chatSection" class="hide" style="padding-top:12px">
        <div class="side-cards">
          <div class="side-card">
            <div class="side-card-title">🎯 Today's focus</div>
            <div class="side-card-body" id="focusSummary">Sara will summarize your day here.</div>
          </div>
          <div class="side-card">
            <div class="side-card-title">💚 Health note</div>
            <div class="side-card-body" id="healthSummary">Sara will remind you gently about your health.</div>
          </div>
          <div class="side-card">
            <div class="side-card-title">🎙️ Voice</div>
            <div class="side-card-body" id="voiceStatus">Speech ready when supported by your browser.</div>
          </div>
        </div>
        <div class="chat-log" id="chatLog"></div>
      </div>

    </div><!-- content-area -->

    <!-- Quick tool buttons (only in chat mode) -->
    <div class="tool-row hide" id="toolRow">
      <button class="tool-btn" data-prompt="Check on my health and ask me how today is going.">🩺 Health</button>
      <button class="tool-btn" data-prompt="Teach me something interesting about the world today.">🌍 Teach</button>
      <button class="tool-btn" data-prompt="Give me one smart suggestion for today based on my goals.">💡 Suggest</button>
      <button class="tool-btn" data-prompt="Talk to me like a caring friend.">🤝 Friend</button>
    </div>

    <!-- Compose -->
    <div class="compose-area" id="composeArea">
      <textarea class="compose-input" id="message" placeholder="Message Sara…" rows="1"></textarea>
      <button class="btn-icon" id="listenButton" title="Voice input">🎤</button>
      <button class="btn-send" id="sendButton" title="Send">➤</button>
    </div>

    <div class="voice-line">Sara's room · local Python backend · browser voice</div>

  </div><!-- panel-right -->
</div><!-- app -->

<style>
  @keyframes waveArm{
    0%,100%{transform:rotate(0deg)}
    50%{transform:rotate(-20deg)}
  }
</style>

<script>
// ── DOM refs ──────────────────────────────────────────────────────────────
const profileSection = document.getElementById('profileSection');
const chatSection    = document.getElementById('chatSection');
const profileForm    = document.getElementById('profileForm');
const chatLog        = document.getElementById('chatLog');
const message        = document.getElementById('message');
const speechBubble   = document.getElementById('speechBubble');
const voiceStatus    = document.getElementById('voiceStatus');
const focusSummary   = document.getElementById('focusSummary');
const healthSummary  = document.getElementById('healthSummary');
const dailyPromptText= document.getElementById('dailyPromptText');
const statusSub      = document.getElementById('statusSub');
const modePill       = document.getElementById('modePill');
const moodPill       = document.getElementById('moodPill');
const healthPill     = document.getElementById('healthPill');
const listenButton   = document.getElementById('listenButton');
const sendButton     = document.getElementById('sendButton');
const toolRow        = document.getElementById('toolRow');
const clockDisplay   = document.getElementById('clockDisplay');

let currentProfile   = null;
let proactiveTimer   = null;

// ── Clock ─────────────────────────────────────────────────────────────────
function updateClock(){
  const now = new Date();
  const h = String(now.getHours()).padStart(2,'0');
  const m = String(now.getMinutes()).padStart(2,'0');
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  clockDisplay.textContent = days[now.getDay()] + ' ' + h + ':' + m;
}
updateClock();
setInterval(updateClock, 30000);

// ── Bubble & speech ───────────────────────────────────────────────────────
function setBubble(text){
  speechBubble.style.animation = 'none';
  speechBubble.offsetHeight;
  speechBubble.style.animation = 'bubblePop .4s cubic-bezier(.34,1.56,.64,1)';
  speechBubble.textContent = text.length > 120 ? text.slice(0,117)+'…' : text;
}

function isHindi(text){ return /[\u0900-\u097F]/.test(text) }

function chooseSaraVoice(text){
  const voices = window.speechSynthesis.getVoices();
  const hindi = isHindi(text);
  const hindiR = [/heera/i,/kalpana/i,/swara/i,/hindi/i,/hi-in/i];
  const enR    = [/female/i,/zira/i,/aria/i,/susan/i,/samantha/i,/victoria/i,/karen/i,/google uk english female/i];
  const rules  = hindi ? hindiR : enR;
  for(const r of rules){ const v=voices.find(v=>r.test(v.name)||r.test(v.lang)); if(v)return v; }
  if(hindi) return voices.find(v=>/hi-|hindi/i.test(v.lang))||voices[0];
  return voices.find(v=>/en-(gb|us|in)/i.test(v.lang))||voices[0];
}

function say(text){
  if(!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const clean = text.replace(/[^\w\s\u0900-\u097F,.!?'-]/g,' ').replace(/\s+/g,' ').trim();
  const u = new SpeechSynthesisUtterance(clean);
  u.rate=.9; u.pitch=1.12;
  const v = chooseSaraVoice(clean);
  if(v) u.voice=v;
  u.onstart=()=> voiceStatus.textContent = v?'Sara is speaking with '+v.name+'.':'Sara is speaking.';
  u.onend=()=> voiceStatus.textContent = v?'Voice ready: '+v.name:'Speech ready.';
  window.speechSynthesis.speak(u);
}

// ── Chat bubbles ──────────────────────────────────────────────────────────
function addBubble(role, text, speak=false){
  const d = document.createElement('div');
  d.className = 'bubble ' + (role==='sara' ? 'bubble-sara' : 'bubble-user');
  d.textContent = text;
  chatLog.appendChild(d);
  chatLog.scrollTop = chatLog.scrollHeight;
  document.getElementById('contentArea').scrollTop = document.getElementById('contentArea').scrollHeight;
  if(role==='sara'){ setBubble(text); if(speak) say(text); }
}

// ── Activate chat mode ────────────────────────────────────────────────────
function setMode(p){
  currentProfile = p;
  profileSection.classList.add('hide');
  chatSection.classList.remove('hide');
  toolRow.classList.remove('hide');
  statusSub.textContent = 'Friend mode · ' + p.name;
  modePill.textContent  = '🌿 Active';
  moodPill.textContent  = '😊 ' + (p.mood||'—');
  healthPill.textContent= '💚 ' + (p.health ? p.health.slice(0,20) : '—');
  focusSummary.textContent  = p.today  ? 'Today: '+p.today  : 'Tell Sara what is happening today.';
  healthSummary.textContent = p.health ? 'Health: '+p.health : 'Tell Sara how your body and energy feel.';
  dailyPromptText.textContent = 'Sara is ready to support ' + p.name + ' today.';
  startChecks();
}

function fillForm(p){
  Object.entries(p).forEach(([k,v])=>{ const f=document.getElementById(k); if(f)f.value=v; });
}

// ── API helpers ───────────────────────────────────────────────────────────
async function sendMessage(msg, speak=true){
  addBubble('user', msg);
  const r = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
  const d = await r.json();
  addBubble('sara', d.reply, speak);
  if(d.focus_summary)  focusSummary.textContent  = d.focus_summary;
  if(d.health_summary) healthSummary.textContent = d.health_summary;
}

async function loadProfile(){
  const r = await fetch('/api/profile');
  const d = await r.json();
  if(!d.profile) return;
  fillForm(d.profile);
  setMode(d.profile);
  addBubble('sara','नमस्ते '+d.profile.name+', मैं सारा हूँ। मैं आपकी health, आज का दिन और goals समझकर आपसे दोस्त की तरह बात करूँगी।',true);
}

function startChecks(){
  if(proactiveTimer) clearInterval(proactiveTimer);
  proactiveTimer = setInterval(async()=>{
    if(!currentProfile||document.hidden) return;
    const r = await fetch('/api/checkin');
    const d = await r.json();
    if(d.message){
      addBubble('sara',d.message,false);
      if(d.focus_summary)  focusSummary.textContent  = d.focus_summary;
      if(d.health_summary) healthSummary.textContent = d.health_summary;
    }
  },45000);
}

// ── Events ────────────────────────────────────────────────────────────────
profileForm.addEventListener('submit', async e=>{
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(profileForm).entries());
  const r = await fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const d = await r.json();
  setMode(d.profile);
  chatLog.innerHTML='';
  addBubble('sara',d.message,true);
});

sendButton.addEventListener('click', async ()=>{
  const m = message.value.trim();
  if(!m) return;
  message.value='';
  await sendMessage(m,true);
});

message.addEventListener('keydown', async e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendButton.click(); }
});

document.querySelectorAll('[data-prompt]').forEach(b=>{
  b.addEventListener('click',()=>{ message.value=b.dataset.prompt; message.focus(); });
});

document.querySelectorAll('[data-checkin]').forEach(b=>{
  b.addEventListener('click', async()=>{
    if(!currentProfile){ message.value=b.dataset.checkin; message.focus(); return; }
    await sendMessage(b.dataset.checkin,true);
  });
});

// Voice input
const SR = window.SpeechRecognition||window.webkitSpeechRecognition;
if(SR){
  const rec = new SR();
  rec.lang='en-US'; rec.interimResults=false; rec.maxAlternatives=1;
  listenButton.addEventListener('click',()=>{ rec.start(); voiceStatus.textContent='Listening…'; });
  rec.onresult=e=>{ message.value=e.results[0][0].transcript; voiceStatus.textContent='Voice captured. Send it now.'; };
  rec.onerror=()=> voiceStatus.textContent='Voice error. You can still type.';
  rec.onend=()=>{ if(!message.value.trim()) voiceStatus.textContent='Speech ready.'; };
} else {
  listenButton.disabled=true;
  voiceStatus.textContent='Voice input not supported, but Sara can still speak.';
}

// Load voices async
if('speechSynthesis' in window){
  window.speechSynthesis.onvoiceschanged = ()=>{};
}

loadProfile().catch(()=>{});
</script>
</body>
</html>
"""


def load_profile():
    if not PROFILE_PATH.exists():
        return None
    try:
        data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def save_profile(profile):
    PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def normalize_profile(data):
    fields = ["name", "city", "age", "mood", "health", "today", "interests", "goals", "routine"]
    profile = {f: str(data.get(f, "")).strip() for f in fields}
    profile["name"] = profile["name"] or "friend"
    profile["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return profile


def focus_summary(profile):
    return f"Today: {profile.get('today') or 'No plan shared yet.'} | Goal path: {profile.get('goals') or 'No goals shared yet.'}"


def health_summary(profile):
    return f"Health: {profile.get('health') or 'No health note shared yet.'} | Mood: {profile.get('mood') or 'unknown mood'}"


def welcome(profile):
    bits = []
    if profile.get("city"):
        bits.append(f"from {profile['city']}")
    if profile.get("interests"):
        bits.append(f"interested in {profile['interests']}")
    if profile.get("goals"):
        bits.append(f"working toward {profile['goals']}")
    if profile.get("today"):
        bits.append(f"handling {profile['today']} today")
    detail = ", ".join(bits) if bits else "ready to begin"
    return f"Hi {profile['name']}. I am Sara. I know you are {detail}. I will check on your health, ask how your day is going, teach you little things about the world, and help you make kind smart decisions."


def lesson():
    return random.choice([
        "World lesson: forests cool land, protect soil, and hold water, so they shape climate as well as beauty.",
        "World lesson: trade routes changed food, clothing, and language, which is why cultures often carry traces of distant places.",
        "World lesson: the Moon is about 384,400 kilometers away, so moonlight is sunlight reflected from a very distant rocky world.",
        "World lesson: memory improves more with sleep, repetition, and active recall than with passive rereading.",
    ])


def suggestion(profile):
    interests = profile.get("interests", "").lower()
    goals = profile.get("goals", "").lower()
    routine = profile.get("routine", "").lower()
    today = profile.get("today", "").lower()
    age = profile.get("age", "").lower()
    if "code" in interests or "software" in goals or "engineer" in goals:
        return "Suggestion: build one small thing today that you can finish. Tiny shipped work teaches more than a big unfinished dream."
    if "study" in goals or "student" in age or "class" in today:
        return "Suggestion: study in short focused rounds and explain each topic back in your own words."
    if "health" in goals or "exercise" in routine or "fitness" in interests:
        return "Suggestion: protect your energy first. Water, a short walk, and one simple meal upgrade can change the whole day."
    if "busy" in today or "meeting" in today:
        return "Suggestion: choose one non-negotiable task for today and let the rest be flexible. Clarity lowers stress."
    return "Suggestion: do one meaningful task, one body-care action, and one quiet reset for your mind today."


def friend_check(profile):
    mood = profile.get("mood") or "a little uncertain"
    return f"Hey {profile['name']}, I am with you. You mentioned feeling {mood}. Keep today kind and real: care for your body, finish one meaningful thing, and do not measure your worth only by output."


def proactive(profile):
    return random.choice([
        f"Little check-in, {profile['name']}: have you had water, stretched a little, and taken one calm breath today?",
        f"{profile['name']}, what is the one thing happening today that matters most? I can help you make it feel lighter.",
        f"Gentle reminder, {profile['name']}: if your energy is low, simplify the plan before blaming yourself.",
        f"{profile['name']}, how is your health today: sleep, food, water, movement, and stress? I care about all of it.",
    ])


def welcome_hi(profile):
    return f"Namaste {profile['name']}, main Sara hoon. Main aapki health, aaj ka din, goals aur routine ke hisaab se aapse dosti se baat karungi."


def lesson_hi():
    return random.choice([
        "Duniya ki ek baat: jungle hawa ko thanda rakhne, mitti bachane aur paani sambhalne mein bahut madad karte hain.",
        "Duniya ki ek baat: purane trade routes ne khane, kapde aur bhasha ko bahut prabhavit kiya tha.",
        "Duniya ki ek baat: chaand ki roshni asal mein suraj ki roshni hoti hai jo chaand se takra kar aati hai.",
        "Duniya ki ek baat: padhai tab zyada yaad rehti hai jab aap break lekar repeat karte ho aur khud se recall karte ho.",
    ])


def suggestion_hi(profile):
    interests = profile.get("interests", "").lower()
    goals = profile.get("goals", "").lower()
    today = profile.get("today", "").lower()
    age = profile.get("age", "").lower()
    if "code" in interests or "software" in goals or "engineer" in goals:
        return "Suggestion: aaj ek chhota sa feature complete karo. Chhoti finished cheezein bade incomplete plans se better hoti hain."
    if "study" in goals or "student" in age or "class" in today:
        return "Suggestion: padhai ko short focused rounds mein karo aur phir topic ko apne words mein samjhao."
    return "Suggestion: aaj ek important kaam, ek health-care action, aur ek chhota mind reset zaroor karo."


def friend_check_hi(profile):
    mood = profile.get("mood") or "thoda uncertain"
    return f"{profile['name']}, main aapke saath hoon. Aapne bataya ki aap {mood} mehsoos kar rahe ho. Aaj apne body ka khayal rakho, ek meaningful kaam complete karo, aur khud par zyada pressure mat daalo."


def proactive_hi(profile):
    return random.choice([
        f"{profile['name']}, paani piya kya? Thoda stretch bhi kar lo.",
        f"{profile['name']}, aaj ka sabse important kaam kaunsa hai? Main usse simple banane mein help kar sakti hoon.",
        f"{profile['name']}, agar energy low hai to plan ko easy banao, khud ko blame mat karo.",
        f"{profile['name']}, sleep, food, water aur stress ka kya haal hai aaj?",
    ])


def reply_hi(message, profile):
    m = message.lower()
    name = profile.get("name", "friend")
    if any(x in m for x in ["health", "body", "sleep", "water", "food", "energy", "tabiyat", "sehat"]):
        return f"{name}, aapki health sabse pehle aati hai. Paani, thoda khana, aur aaj ke liye gentle pace rakho. {suggestion_hi(profile)}"
    if any(x in m for x in ["aaj", "today", "schedule", "din"]):
        return f"{name}, aaj ke 3 sabse important kaam batao, main unhe simple kar dungi. Filhal: {suggestion_hi(profile)}"
    if any(x in m for x in ["duniya", "world", "seekhao", "teach", "fact"]):
        return lesson_hi()
    if any(x in m for x in ["suggest", "advice", "kya karu", "recommend"]):
        return suggestion_hi(profile)
    if any(x in m for x in ["friend", "sad", "tired", "stressed", "motivate", "udaas"]):
        return friend_check_hi(profile)
    return f"{name}, main samajh rahi hoon. {suggestion_hi(profile)}\n\n{lesson_hi()}\n\n{friend_check_hi(profile)}"


def reply(message, profile):
    m = message.lower()
    name = profile.get("name", "friend")
    if any(x in m for x in ["health", "body", "sick", "exercise", "sleep", "water", "food", "energy"]):
        return f"{name}, your health matters first. Start with the basics: water, a little food if you have not eaten, and honest pacing. {suggestion(profile)}"
    if any(x in m for x in ["today", "day", "schedule"]):
        return f"{name}, tell me the three biggest parts of your day and I will help you simplify them. For now: {suggestion(profile)}"
    if any(x in m for x in ["teach", "learn", "world", "fact", "explain"]):
        return lesson()
    if any(x in m for x in ["suggest", "advice", "recommend", "what should i do"]):
        return suggestion(profile)
    if any(x in m for x in ["friend", "check in", "sad", "tired", "lonely", "stressed", "motivate"]):
        return friend_check(profile)
    if any(x in m for x in ["goal", "plan", "routine", "habit", "productive"]):
        return f"{name}, choose the next visible step, not the whole mountain. Put that one step on today's timeline, and protect your energy while doing it."
    if any(x in m for x in ["hello", "hi", "hey"]):
        return f"Hello {name}. I am here. Want a health check-in, a world lesson, or a smart plan for today?"
    return f"{name}, I hear you. {suggestion(profile)}\n\n{lesson()}\n\n{friend_check(profile)}"


def localized_welcome(profile):
    return welcome_hi(profile)


def localized_proactive(profile):
    return proactive_hi(profile)


def localized_reply(message, profile):
    return reply_hi(message, profile)


class SaraHandler(BaseHTTPRequestHandler):
    def _json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, payload):
        body = payload.encode("utf-8")
        self.send_response(200)
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
            self._html(HTML_PAGE)
            return
        if path == "/api/profile":
            self._json({"profile": load_profile()})
            return
        if path == "/api/checkin":
            profile = load_profile()
            if not profile:
                self._json({"message": None})
                return
            self._json({
                "message": localized_proactive(profile),
                "focus_summary": focus_summary(profile),
                "health_summary": health_summary(profile)
            })
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/profile":
            profile = normalize_profile(self._read_json())
            save_profile(profile)
            self._json({
                "profile": profile,
                "message": localized_welcome(profile),
                "focus_summary": focus_summary(profile),
                "health_summary": health_summary(profile)
            })
            return
        if path == "/api/chat":
            profile = load_profile()
            if not profile:
                self._json(
                    {"reply": "Please tell me about yourself first so I can be more personal with you."},
                    status=HTTPStatus.BAD_REQUEST
                )
                return
            message = str(self._read_json().get("message", "")).strip()
            if not message:
                self._json({"reply": "I am listening. Tell me what is going on with you today."})
                return
            if any(x in message.lower() for x in ["i feel", "today i", "my health", "sleep", "stress", "energy"]):
                profile["mood"] = message[:160]
                profile["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_profile(profile)
            self._json({
                "reply": localized_reply(message, profile),
                "focus_summary": focus_summary(profile),
                "health_summary": health_summary(profile)
            })
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

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
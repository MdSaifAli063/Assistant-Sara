# 🌸 Sara — Your Bilingual Room Companion

> **A beautiful AI-powered virtual room companion** — Sara lives in a hand-crafted 3D room, speaks both **Hindi and English**, checks on your health, guides your day, and stays with you like a real friend.

---

## ✨ What Sara Can Do

| Feature | Description |
|---|---|
| 🏠 **3D Room** | Hand-crafted CSS 3D room — back wall, side walls, wood floor, fairy lights, bookshelf, window with scenery, rug, desk |
| 👩🏽 **Beautiful Avatar** | Detailed Indian girl in a vibrant teal Lehenga Choli — hair bun with flowers, jewelry, mehendi, maang tikka |
| 🗣️ **Bilingual Voice** | Sara speaks **Hindi + English**, auto-detecting language in each sentence and using the best available voice |
| 🎤 **Voice Input** | Speak to Sara in Hindi or English — click the mic button |
| 💚 **Health Check-ins** | Sara asks about sleep, energy, water, food, stress proactively every 45 seconds |
| 🌍 **World Lessons** | Random interesting world facts in your chosen language |
| 💡 **Smart Suggestions** | Personalized suggestions based on your goals, interests, and routine |
| 🤝 **Friend Mode** | Caring, emotionally warm replies tailored to your mood |
| 🌗 **Language Toggle** | Switch between Hindi 🇮🇳 and English 🇬🇧 at any time |

---

## 🚀 Getting Started

### Requirements

- Python 3.8 or higher
- A modern browser (Chrome, Edge, or Safari recommended for best voice support)
- No additional Python packages needed — uses only the standard library

### Run Sara

```bash
# 1. Save sara_server.py anywhere on your computer

# 2. Open your terminal / command prompt and run:
python sara_server.py

# 3. Open your browser and go to:
http://127.0.0.1:8010
```

You will see:

```
✨ Sara is ready at http://127.0.0.1:8010
   Profile stored at: /your/path/sara_profile.json
   Press Ctrl+C to stop.
```

---

## 🗂️ Files

```
sara_server.py       ← The only file you need to run Sara
sara_profile.json    ← Auto-created when you save your profile (stores your info locally)
README.md            ← This file
```

---

## 🎙️ Voice System — How It Works

Sara uses the **Web Speech API** built into your browser — no API keys or subscriptions needed.

### Speaking (Text-to-Speech)

Sara automatically **splits her responses** into Hindi and English segments and reads each segment with the most appropriate voice:

- **Hindi text** → Uses `hi-IN` voices (Heera, Kalpana, Swara, or any available Hindi voice)
- **English text** → Uses female English voices (Samantha, Karen, Aria, etc.)
- **Mixed replies** → Each sentence is spoken in the right language automatically

### Listening (Speech-to-Text)

1. Click the **🎤 microphone button**
2. Speak in Hindi or English (Sara uses whichever language you've selected in the toggle)
3. Your speech appears in the text box — click **➤** to send

### Replay Last Reply

Click the **🔊 speaker button** to replay Sara's last response.

### Browser Voice Quality

| Browser | Hindi Voice Quality | English Voice Quality |
|---|---|---|
| **Chrome** | ✅ Best (Google Hindi) | ✅ Excellent |
| **Edge** | ✅ Very good (Microsoft voices) | ✅ Excellent |
| **Safari (Mac)** | ⚠️ Limited | ✅ Good (Samantha) |
| **Firefox** | ⚠️ OS voices only | ⚠️ Limited |

> **Tip:** On Windows, install additional TTS voices via **Settings → Time & Language → Speech → Add voices** for better Hindi support.

---

## 🌸 Sara's Room — What's Inside

The 3D room is built entirely with **CSS 3D transforms** and **SVG** — no images, no canvas, no WebGL.

| Room Element | Details |
|---|---|
| 🪟 **Window** | Animated clouds, rolling hills, 3 trees, animated sun, pink curtains with valance, flower box with emoji flowers |
| 📚 **Bookshelf** | 3 rows of colorful books, mini globe, small plant |
| 🪑 **Desk** | Wood surface, laptop (glowing screen), notebook, steaming tea mug (animated steam), potted plant, desk lamp with warm glow |
| 🎨 **Wall Decor** | Abstract picture frame, live wall clock |
| 💡 **Fairy Lights** | Animated SVG string lights across the top of the wall (10 colored bulbs) |
| 🟣 **Rug** | Vibrant purple/pink rug on the wood floor |
| 🌿 **Side Walls** | Perspective-angled walls with wainscoting on the back wall |

---

## 👩🏽 Sara's Appearance

Sara is a beautifully detailed SVG character:

| Feature | Details |
|---|---|
| 👗 **Dress** | Vibrant teal Lehenga Choli with gold embroidery, dupatta, coral choli blouse |
| 💄 **Face** | Almond-shaped eyes, kajal liner, thick eyebrows, natural blush, nose ring (nath), bindi |
| 💍 **Jewelry** | Maang tikka, gold necklace with pendants, jhumka earrings, bangles, anklets |
| 💅 **Mehendi** | Subtle mehendi pattern on hand |
| 💐 **Hair** | Long dark hair in a bun with pink and gold flowers |
| 🌟 **Animations** | Floating idle, waving right hand, flowing dupatta |

---

## 📱 Responsive Design

- **Desktop (1200px+):** Side-by-side room + panel layout
- **Tablet (900px):** Room on top, panel below
- **Mobile:** Stacked layout with scrollable panel

---

## 🔧 Customization

### Change Language Default

Edit line near the bottom of `sara_server.py`:

```python
# In normalize_profile():
p["lang"] = str(data.get("lang","hi")).strip()  # Change "hi" to "en" for English default
```

### Change Port

```python
PORT = 8010  # Change to any available port
```

### Add New Replies

Add to the reply functions in `sara_server.py`:

```python
def reply_hi(msg, p):
    m = msg.lower()
    # Add your own keyword checks:
    if any(x in m for x in ["coding","code"]):
        return "Wah! Coding bahut achha kaam hai..."
    # ... existing replies ...
```

### Add New World Facts

```python
def lesson_hi():
    return random.choice([
        "🌍 Duniya ki ek baat: aapka fact yahan...",
        # Add more facts here
    ])
```

---

## 🛡️ Privacy

- **All data stays on your computer.** Sara stores your profile in `sara_profile.json` locally.
- **No external API calls** — no data is sent to any server.
- **No tracking, no analytics, no ads.**

---

## ❓ Troubleshooting

**Sara's voice is not working:**
- Make sure you're using Chrome or Edge for the best voice support
- Check that your browser has permission to use audio
- On first load, click anywhere on the page before Sara tries to speak (browser autoplay policy)

**Hindi voice sounds robotic or switches to English:**
- Install Hindi voices in your OS:
  - **Windows:** Settings → Time & Language → Speech → Add voices → search "Hindi"
  - **Mac:** System Preferences → Accessibility → Speech → System Voice → Manage voices
  - **Linux:** Install `espeak-ng` with Hindi support

**Voice input not working:**
- Chrome/Edge required for `SpeechRecognition`
- Allow microphone access when the browser asks
- Make sure you're on `http://127.0.0.1:8010` (not a file:// URL)

**Port already in use:**
```bash
# Change PORT in sara_server.py, or kill the existing process:
# Windows:
netstat -ano | findstr :8010
taskkill /PID <pid> /F

# Mac/Linux:
lsof -i :8010
kill -9 <pid>
```

---

## 💡 Tips for Best Experience

1. **Use Chrome on Windows** — best Hindi voice support
2. **Fill your profile completely** — the more Sara knows, the more personal her replies
3. **Try the mood buttons** — quick check-ins are the best way to start the day
4. **Use the tool buttons** (Health / Teach / Suggest / Friend) for instant topic-specific chats
5. **Click 🔊 to replay** Sara's last message anytime
6. **Switch languages mid-conversation** — use the Hindi/English toggle at any time

---

## 🌸 Made with Love

Sara is built with:
- **Python** standard library only (no pip install needed)
- **Pure HTML, CSS, JS** — no frameworks, no bundler
- **CSS 3D transforms** for the room
- **SVG** for Sara's avatar
- **Web Speech API** for voice (browser built-in, free)

---

*Sara is always in her room, waiting to talk. Namaste! 🙏*
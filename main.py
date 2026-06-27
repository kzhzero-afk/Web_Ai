from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import os
import shutil
import requests
import json
import base64
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, vfx

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔑 သင့်ရဲ့ AQ. Key အမှန်စစ်စစ်
API_KEY = os.getenv("AQ.Ab8RN6KezttKmwn79SYVncxe6wpJ9TrnEao1FqlyRfrgw8crOA")

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <head>
        <title>Auto Video Recap System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #1a1b26; color: #a9b1d6; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #24283b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
            h1 { text-align: center; color: #7aa2f7; font-size: 24px; margin-bottom: 25px; }
            .section-title { background: #414868; padding: 8px 12px; border-radius: 6px; font-weight: bold; color: #ff9e64; margin-top: 20px; margin-bottom: 15px; display: inline-block; }
            .grid { display: block; }
            @media (min-width: 600px) {
                .grid { display: table; width: 100%; table-layout: fixed; }
                .col { display: table-cell; width: 50%; padding: 10px; vertical-align: top; }
            }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-size: 14px; color: #9ece6a; }
            select, input[type="file"], input[type="range"] { width: 100%; padding: 10px; background: #1f2335; border: 1px solid #3b4261; border-radius: 6px; color: #c0caf5; box-sizing: border-box; }
            .radio-group { display: flex; gap: 10px; }
            .radio-btn { background: #1f2335; padding: 10px 15px; border-radius: 6px; border: 1px solid #3b4261; cursor: pointer; flex: 1; text-align: center; }
            .radio-btn input { display: none; }
            .radio-btn:has(input:checked) { background: #7aa2f7; color: #1a1b26; font-weight: bold; }
            .submit-btn { width: 100%; background: linear-gradient(90deg, #7aa2f7, #bb9af7); color: #1a1b26; border: none; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 25px; box-shadow: 0 0 15px rgba(122, 162, 247, 0.4); }
            .submit-btn:hover { opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ Auto-Synced Video Recap Creator ✨</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label>📁 မူရင်းဗီဒီယို ထည့်ရန် (Upload Video)</label>
                    <input type="file" name="file" accept="video/*" required>
                </div>
                <div class="grid">
                    <div class="col">
                        <div class="section-title">ဖြတ်မည့် အမျိုးအစား & Zoom</div>
                        <div class="form-group">
                            <label>ဗီဒီယို Ratio</label>
                            <select name="ratio">
                                <option value="916">9:16 (TikTok/Reels)</option>
                                <option value="43">4:3 (Classic)</option>
                                <option value="169">16:9 (Landscape)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Zoom Level</label>
                            <select name="zoom_level">
                                <option value="1.0">1x (No Zoom)</option>
                                <option value="1.2">1.2x</option>
                                <option value="1.5">1.5x</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Mirror Flip (ဘယ်/ညာ လှန်မည်)</label>
                            <select name="mirror">
                                <option value="false">မလှန်ပါ (None)</option>
                                <option value="true">ဘယ်ညာလှန်မည် (Flip X)</option>
                            </select>
                        </div>
                    </div>
                    <div class="col">
                        <div class="section-title">ဇာတ်လမ်းပြောမည့် အသံနှင့် စတိုင်</div>
                        <div class="form-group">
                            <label>အသံဇာတ်ကောင် (Voice)</label>
                            <select name="voice_lang">
                                <option value="my">မြန်မာအသံ (Myanmar)</option>
                                <option value="en">အင်္ဂလိပ်အသံ (English)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>ဇာတ်ကြောင်းပြောမည့် စတိုင် (Narrative Style)</label>
                            <select name="style">
                                <option value="third_person">Third-Person (သူ/သူမ - ဇာတ်လမ်းပြောပုံစံ)</option>
                                <option value="first_person">First-Person (ကျွန်တော်/ကျွန်မ စတိုင်)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>အသံ မြန်နှုန်း (TTS Speed %)</label>
                            <input type="range" name="tts_speed" min="0.8" max="1.5" step="0.1" value="1.0">
                        </div>
                    </div>
                </div>
                <div class="form-group" style="padding: 0 10px;">
                    <div class="section-title">ဇာတ်လမ်း အသေးစိတ်မှု (Script Detail Level)</div>
                    <div class="radio-group">
                        <label class="radio-btn"><input type="radio" name="detail" value="short" checked> အတိုချုပ် (Short)</label>
                        <label class="radio-btn"><input type="radio" name="detail" value="normal"> ပုံမှန် (Normal)</label>
                        <label class="radio-btn"><input type="radio" name="detail" value="detailed"> အသေးစိတ် (Detailed)</label>
                    </div>
                </div>
                <button type="submit" class="submit-btn">✨ Create Auto-Synced Video ✨</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    ratio: str = Form(...),
    zoom_level: float = Form(...),
    mirror: str = Form(...),
    voice_lang: str = Form(...),
    style: str = Form(...),
    tts_speed: float = Form(...),
    detail: str = Form(...)
):
    video_name = file.filename
    base_name = os.path.splitext(video_name)[0]
    
    orig_video_path = os.path.join(UPLOAD_D

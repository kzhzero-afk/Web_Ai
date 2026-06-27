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
API_KEY = "AQ.Ab8RN6Kj40EICZHjNSVPhRIBSK6otwVncxe6wpJ9TrnEao1FqlyRfrgw8crOA"

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
            <h1>✨ Thandar Aung Auto Recap </h1>
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
    
    orig_video_path = os.path.join(UPLOAD_DIR, f"orig_{video_name}")
    extracted_audio_path = os.path.join(UPLOAD_DIR, f"extracted_{base_name}.mp3")
    temp_audio_path = os.path.join(UPLOAD_DIR, f"temp_{base_name}.mp3")
    output_video_name = f"recap_{base_name}.mp4"
    output_video_path = os.path.join(UPLOAD_DIR, output_video_name)
    
    with open(orig_video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # --- အဆင့် ၁: ဗီဒီယိုထဲမှ အသံကို သီးသန့်ဆွဲထုတ်ခြင်း ---
        print("Extracting audio from video...")
        video_clip = VideoFileClip(orig_video_path)
        
        has_audio = video_clip.audio is not None
        if has_audio:
            video_clip.audio.write_audiofile(extracted_audio_path, logger=None)
            with open(extracted_audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
        else:
            audio_base64 = ""

        # --- အဆင့် ၂: AQ Key များအတွက် သီးသန့်ထုတ်လုပ်ထားသော v1 Stable Endpoint သို့ ပို့ခြင်း ---
        length_prompt = "1-2 short sentences" if detail == "short" else "3-4 sentences" if detail == "normal" else "detailed paragraphs"
        prompt_lang = "Burmese (မြန်မာဘာသာ)" if voice_lang == "my" else "English"
        
        prompt = f"""
        Act as a professional movie story narrator. Based on the provided audio context,
        provide a {detail} recap/summary in {prompt_lang} using {style} style.
        The length must be around {length_prompt}.
        Do not use markdown formatting like asterisks. Output clean plain text only.
        """

        # 💡 ကမ္ဘာသုံး စံနှုန်းဝင် v1 Stable URL Endpoint သို့ ပြောင်းလဲလိုက်ပါပြီ (v1beta မဟုတ်တော့ပါ)
        gen_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }

        parts = [{"text": prompt}]
        if has_audio and audio_base64:
            parts.append({
                "inline_data": {
                    "mime_type": "audio/mp3",
                    "data": audio_base64
                }
            })

        payload = {"contents": [{"parts": parts}]}
        
        print("Generating recap via Gemini Stable v1 API...")
        gen_res = requests.post(gen_url, json=payload, headers=headers)
        
        if gen_res.status_code != 200:
            return {"status": "failed", "stage": "generate", "code": gen_res.status_code, "error": gen_res.text}
            
        recap_text = gen_res.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Generated Script: {recap_text}")

        # --- အဆင့် ၃: TTS နှင့် ဗီဒီယို ပြန်လည်တည်းဖြတ်ခြင်း ---
        tts = gTTS(text=recap_text, lang=voice_lang, slow=False)
        tts.save(temp_audio_path)

        voiceover_clip = AudioFileClip(temp_audio_path)

        if mirror == "true":
            video_clip = video_clip.fx(vfx.mirror_x)

        if zoom_level > 1.0:
            video_clip = video_clip.resize(zoom_level)

        if has_audio:
            combined_audio = CompositeAudioClip([video_clip.audio.volumex(0.2), voiceover_clip.volumex(1.8)])
        else:
            combined_audio = voiceover_clip

        final_clip = video_clip.set_audio(combined_audio)
        final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", threads=2, preset='ultrafast', logger=None)

        video_clip.close()
        voiceover_clip.close()
        final_clip.close()
        
        # ယာယီဖိုင်များ ရှင်းလင်းခြင်း
        if os.path.exists(orig_video_path): os.remove(orig_video_path)
        if os.path.exists(extracted_audio_path): os.remove(extracted_audio_path)
        if os.path.exists(temp_audio_path): os.remove(temp_audio_path)

        return HTMLResponse(f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #1a1b26; color: #a9b1d6; text-align:center; padding-top:50px; }}
                .result-box {{ background: #24283b; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; }}
                video {{ width: 100%; border-radius: 8px; margin-top: 15px; }}
                .download-btn {{ display: inline-block; padding: 12px 24px; background: #9ece6a; color: #1a1b26; font-weight:bold; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="result-box">
                <h2>🎉 Auto-Synced Video Ready!</h2>
                <p><strong>Script Detail ({detail}):</strong> {recap_text}</p>
                <video controls>
                    <source src="/download/{output_video_name}" type="video/mp4">
                </video>
                <br>
                <a href="/download/{output_video_name}" download class="download-btn">📥 Download Recap Video</a>
                <br><br>
                <a href="/" style="color: #7aa2f7;">Back to Dashboard</a>
            </div>
        </body>
        </html>
        """)

    except Exception as e:
        if os.path.exists(orig_video_path): os.remove(orig_video_path)
        if os.path.exists(extracted_audio_path): os.remove(extracted_audio_path)
        if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
        return {"status": "failed", "error": str(e)}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    return {"error": "File not found"}
    

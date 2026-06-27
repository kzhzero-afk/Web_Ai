from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import os
import shutil
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, vfx
from google import genai
from google.genai import types

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔑 သင်ပေးထားသော Key ကို အသေထည့်သွင်းထားသည်
API_KEY = "AQ.Ab8RN6KezttKmwn79SYVncxe6wpJ9TrnEao1FqlyRfrgw8crOA"
client = genai.Client(api_key=API_KEY)

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <body>
        <h1>Auto-Synced Video Recap</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="video/*" required>
            <button type="submit">Create Recap</button>
        </form>
    </body>
    </html>
    """)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    video_path = os.path.join(UPLOAD_DIR, file.filename)
    audio_path = os.path.join(UPLOAD_DIR, "audio_temp.mp3")
    output_path = os.path.join(UPLOAD_DIR, f"recap_{file.filename}")
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # ၁။ အသံထုတ်ခြင်း
        video = VideoFileClip(video_path)
        if video.audio:
            video.audio.write_audiofile(audio_path, logger=None)
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            # ၂။ Gemini အသစ်ဖြင့် Script ရေးခြင်း
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=["Provide a short, professional movie recap in Burmese.", audio_part]
            )
            recap_text = response.text
            
            # ၃။ TTS လုပ်ခြင်း
            tts = gTTS(text=recap_text, lang='my', slow=False)
            tts.save(audio_path)
            
            # ၄။ ဗီဒီယို ပြန်ပေါင်းခြင်း
            voiceover = AudioFileClip(audio_path)
            final_clip = video.set_audio(voiceover)
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            return FileResponse(output_path)
        return {"error": "Video has no audio"}
    except Exception as e:
        return {"error": str(e)}
        

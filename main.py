from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <head>
        <title>AI Video App</title>
    </head>
    <body style="font-family: Arial; text-align:center; margin-top:80px;">
        <h1>🚀 AI Video Upload System</h1>

        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required><br><br>

            <select name="model">
                <option value="whisper">Whisper</option>
                <option value="google">Google STT</option>
                <option value="gemini">Gemini</option>
            </select><br><br>

            <select name="speed">
                <option value="fast">Fast</option>
                <option value="balanced">Balanced</option>
                <option value="high">High</option>
            </select><br><br>

            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    """)

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    model: str = Form(...),
    speed: str = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "uploaded",
        "file": file.filename,
        "model": model,
        "speed": speed
    }

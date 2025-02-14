
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import whisper
import numpy as np
#import soundfile as sf
import io
from pydub import AudioSegment
import uvicorn
import tempfile
import numpy as np

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
model = whisper.load_model("base")

def convert_to_wav(file: UploadFile):
    audio = AudioSegment.from_file(file.file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        audio.export(temp_wav.name, format="wav")
        return temp_wav.name

def analyze_noise(audio_path: str):
    audio = AudioSegment.from_wav(audio_path)
    samples = np.array(audio.get_array_of_samples())
    rms = np.sqrt(np.mean(samples**2))
    max_rms = np.sqrt(np.mean((np.iinfo(samples.dtype).max)**2))
    noise_level = rms / max_rms
    return noise_level

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    wav_path = convert_to_wav(file)
    result = model.transcribe(wav_path)
    transcription = result["text"]
    noise_level = analyze_noise(wav_path)
    is_noisy = noise_level > 0.5  
    return {
        "transcription": transcription,
        "noise_level": float(noise_level),  
        "is_noisy": bool(is_noisy),  
    }
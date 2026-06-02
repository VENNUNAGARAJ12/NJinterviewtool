import customtkinter as ctk
import pyaudiowpatch as pyaudio
import threading
import os
import wave
import io
import time
import numpy as np
from datetime import datetime
from faster_whisper import WhisperModel
from google import genai

# ==========================================
# GOD-MODE V3: THE STRATEGIST
# Advanced Teleprompter with Strategy Routing & Audio Equalizers
# ==========================================

# --- 1. SETUP API & ENVIRONMENT ---
def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val

load_env()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL: GEMINI_API_KEY is missing from .env file!")
    exit()

ai_client = genai.Client(api_key=api_key)

print("Initializing Advanced AI Engines...")
whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("Whisper Engine Online. Dual-Radar Active.")

conversation_history = []
is_generating = False 

# Setup Auto-Logger
LOG_FILE = f"interview_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"--- INTERVIEW LOG INITIATED AT {datetime.now()} ---\n\n")

def save_to_log(text):
    """Saves the interview transcript and AI hints to a text file for review later."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass

# --- 2. ADVANCED UI SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("700x850")
app.title("Interview God-Mode V3: The Strategist")
app.attributes("-topmost", True)

# Header
title_label = ctk.CTkLabel(app, text="SYSTEM READY", text_color="#00FF00", font=("Consolas", 18, "bold"))
title_label.pack(pady=10)

# Audio Visualizers (Equalizers)
eq_frame = ctk.CTkFrame(app, fg_color="transparent")
eq_frame.pack(fill="x", padx=20, pady=5)

ctk.CTkLabel(eq_frame, text="MIC (YOU):", font=("Consolas", 10, "bold"), text_color="#00FF00").grid(row=0, column=0, padx=5, sticky="w")
mic_progress = ctk.CTkProgressBar(eq_frame, width=200, height=10, progress_color="#00FF00", fg_color="#333333")
mic_progress.grid(row=0, column=1, padx=5)
mic_progress.set(0)

ctk.CTkLabel(eq_frame, text="SYSTEM (THEM):", font=("Consolas", 10, "bold"), text_color="#AAAAAA").grid(row=1, column=0, padx=5, sticky="w", pady=5)
sys_progress = ctk.CTkProgressBar(eq_frame, width=200, height=10, progress_color="#AAAAAA", fg_color="#333333")
sys_progress.grid(row=1, column=1, padx=5, pady=5)
sys_progress.set(0)

# Teleprompter Display
ai_hint_box = ctk.CTkTextbox(app, height=450, text_color="#00FFFF", fg_color="#0A0A0A", font=("Consolas", 22, "bold"), wrap="word", border_width=2, border_color="#1A1A1A")
ai_hint_box.pack(padx=20, pady=10, fill="x")
ai_hint_box.insert("0.0", "YOUR LIVE SCRIPT WILL APPEAR HERE...\n")
ai_hint_box.configure(state="disabled")

# Transcript Display
transcript_box = ctk.CTkTextbox(app, height=150, fg_color="#111111", font=("Consolas", 12), border_width=1, border_color="#333333")
transcript_box.pack(padx=20, pady=10, fill="both", expand=True)
transcript_box.tag_config("interviewer", foreground="#AAAAAA")
transcript_box.tag_config("candidate", foreground="#00FF00")
transcript_box.insert("0.0", "Live Background Log...\n\n", "interviewer")
transcript_box.configure(state="disabled")

# --- 3. THE STRATEGY AI ENGINE ---
def load_resume():
    if os.path.exists("resume.txt"):
        with open("resume.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "[No specific resume provided. Assume candidate is a Senior Software Engineer.]"

def fetch_ai_hint():
    global is_generating
    if is_generating: 
        return 
    
    is_generating = True
    app.after(0, lambda: title_label.configure(text="ANALYZING & GENERATING SCRIPT...", text_color="#FFA500"))
    
    user_resume = load_resume()
    history_context = "\n".join(conversation_history[-12:]) # Expanded context window
    
    # THE MASTER PROMPT
    prompt = f"""
    You are a Principal Software Engineer secretly feeding live answers to a candidate during a high-stakes FAANG interview.
    
    YOUR MISSION:
    Analyze the conversation log and the candidate's resume. Provide the EXACT script they must read out loud immediately to impress the interviewer.

    STRATEGY ROUTING PROTOCOL:
    1. If it is a BEHAVIORAL question (e.g., "tell me about a time"): Use the STAR method. Focus on leadership and impact.
    2. If it is a TECHNICAL question (e.g., "how does Kafka work"): Be concise, highly technical, and mention trade-offs.
    3. If it is a SYSTEM DESIGN question: Outline the high-level architecture first, then dive into bottlenecks.

    FORMATTING RULES:
    - Output EXACTLY what the candidate should say. NO quotes. NO labels like "Candidate:".
    - Limit to 3 to 5 flowing, highly intelligent sentences.
    - Sound natural, confident, and deeply experienced.
    
    RESUME: {user_resume}
    
    LIVE CONVERSATION LOG: 
    {history_context}
    """

    def run_api_request():
        global is_generating
        try:
            # Using stable, high-quota 1.5-flash
            response = ai_client.models.generate_content_stream(
                model='gemini-1.5-flash',
                contents=prompt
            )
            
            # Format UI for new answer
            app.after(0, lambda: ai_hint_box.configure(state="normal"))
            app.after(0, lambda: ai_hint_box.delete("0.0", "end"))
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    app.after(0, lambda t=chunk.text: ai_hint_box.insert("end", t))
                    app.after(0, lambda: ai_hint_box.see("end"))
            
            app.after(0, lambda: ai_hint_box.configure(state="disabled"))
            save_to_log(f"\n[AI COPILOT STRATEGY]:\n{full_response}\n")
            
        except Exception as e:
            app.after(0, lambda: title_label.configure(text="NETWORK OVERLOAD - RETRYING SOON", text_color="#FF0000"))
            print(f"API Error: {e}")
        finally:
            is_generating = False
            app.after(0, lambda: title_label.configure(text="LISTENING FOR NEXT TARGET...", text_color="#00FF00"))

    threading.Thread(target=run_api_request, daemon=True).start()

# --- 4. ADVANCED AUDIO TRANSLATOR ---
def process_speech(audio_bytes, rate, channels, speaker_label):
    app.after(0, lambda: title_label.configure(text=f"DECODING {speaker_label.upper()}...", text_color="#00FFFF"))
    
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio_bytes)
    wav_io.seek(0)
    
    try:
        segments, _ = whisper_model.transcribe(wav_io, beam_size=1)
        transcript_text = " ".join([seg.text for seg in segments]).strip()
        word_count = len(transcript_text.split())
        
        # Ignored throat clears and single-word grunts
        if word_count > 2:
            formatted_line = f"{speaker_label}: {transcript_text}"
            conversation_history.append(formatted_line)
            save_to_log(formatted_line)
            
            tag = "candidate" if speaker_label == "Candidate" else "interviewer"
            
            app.after(0, lambda: transcript_box.configure(state="normal"))
            app.after(0, lambda: transcript_box.insert("end", formatted_line + "\n\n", tag))
            app.after(0, lambda: transcript_box.see("end"))
            app.after(0, lambda: transcript_box.configure(state="disabled"))
            
            # TRIGGER AI: Fires when a substantive sentence is spoken.
            # (Override ON: Triggers for both Interviewer and Candidate for testing purposes)
            if (speaker_label == "Interviewer" or speaker_label == "Candidate") and word_count > 4:
                fetch_ai_hint()
            else:
                app.after(0, lambda: title_label.configure(text="LISTENING...", text_color="#00FF00"))
        else:
            app.after(0, lambda: title_label.configure(text="LISTENING...", text_color="#00FF00"))
             
    except Exception as e:
        print(f"Whisper Error ({speaker_label}): {e}")
        app.after(0, lambda: title_label.configure(text="LISTENING...", text_color="#00FF00"))

# --- 5. DUAL-RADAR AUDIO ENGINE WITH UI METERS ---
def audio_listener():
    p = pyaudio.PyAudio()
    
    try:
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        loopback_device = None
        for loopback in p.get_loopback_device_info_generator():
            if default_speakers["name"] in loopback["name"]:
                loopback_device = loopback
                break
    except Exception:
        loopback_device = None

    try:
        mic_device = p.get_default_input_device_info()
    except Exception:
        mic_device = None

    def start_stream_thread(device, is_loopback):
        label = "Interviewer" if is_loopback else "Candidate"
        sample_rate = int(device["defaultSampleRate"])
        channels = device["maxInputChannels"]
        
        # Adaptive Thresholds
        threshold = 40 if is_loopback else 60  
        
        state = {"frames": [], "is_speaking": False, "silence_frames": 0}

        def callback(in_data, frame_count, time_info, status):
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            
            # Update UI Progress Bars (normalized math to make it look smooth)
            bar_val = min(volume / 1000.0, 1.0) 
            if is_loopback:
                app.after(0, lambda: sys_progress.set(bar_val))
            else:
                app.after(0, lambda: mic_progress.set(bar_val))
            
            if volume > threshold:
                state["is_speaking"] = True
                state["silence_frames"] = 0
                state["frames"].append(in_data)
            elif state["is_speaking"]:
                state["silence_frames"] += 1
                state["frames"].append(in_data)
                
                # 15 frames (~1.5 seconds) to prevent API spam
                if state["silence_frames"] > 15:
                    audio_bytes = b''.join(state["frames"])
                    threading.Thread(target=process_speech, args=(audio_bytes, sample_rate, channels, label), daemon=True).start()
                    state["frames"] = []
                    state["is_speaking"] = False
                    state["silence_frames"] = 0
                    
            return (in_data, pyaudio.paContinue)

        stream = p.open(format=pyaudio.paInt16, channels=channels, rate=sample_rate,
                        frames_per_buffer=4000, input=True, input_device_index=device["index"],
                        stream_callback=callback)
        stream.start_stream()
        while stream.is_active():
            time.sleep(0.1)

    if loopback_device:
        threading.Thread(target=start_stream_thread, args=(loopback_device, True), daemon=True).start()
    if mic_device:
        threading.Thread(target=start_stream_thread, args=(mic_device, False), daemon=True).start()

# --- 6. START APPLICATION ---
threading.Thread(target=audio_listener, daemon=True).start()
app.mainloop()
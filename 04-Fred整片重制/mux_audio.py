from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
subprocess.run(['/Users/USER/.local/bin/ffmpeg','-y','-v','error','-i',str(R/'output/deepinfer-fred-picture-render.mp4'),'-i',str(R/'public/voice-original-speed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','94.233333333','-movflags','+faststart',str(R/'output/deepinfer-fred-full-v1.mp4')],check=True)

from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/nvidia-smi")
async def get_nvidia_smi():
    process = subprocess.Popen(
        ["nvidia-smi", "-lms", "500"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return {"data": stdout.decode()}
    else:
        return {"error": stderr.decode()}

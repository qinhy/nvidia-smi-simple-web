import json
import re
import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess
import shlex

app = FastAPI()


from fastapi.staticfiles import StaticFiles

# Mount the static directory to serve index.html
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/stream-nvidia-smi", response_class=StreamingResponse)
def stream_nvidia_smi():
    command = shlex.split("nvidia-smi -lms 500")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    def generate():
        buffer = ""
        start_delimiter = "\+-+\+\n"
        end_delimiter = "\+-+\+-+\+-+\+\n\s+"
        collecting = False  # This flag indicates if we are between the start and end delimiters

        try:
            # Read each line from the subprocess' stdout
            preline = ''
            for line in iter(process.stdout.readline, ''):
                if re.match(start_delimiter, line):
                    collecting = True  # Start collecting lines
                    buffer = line  # Initialize buffer with the start delimiter line
                elif collecting:
                    buffer += line
                    if re.match(end_delimiter, preline+line):
                        collecting = False  # Stop collecting lines
                        # print(buffer)
                        yield f"data: {buffer.encode('utf-8')}\n\n"  # Send the complete block
                        buffer = ""  # Reset buffer for the next block
                preline = line
        finally:
            process.stdout.close()
            process.wait()

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'text/event-stream',
        'Connection': 'keep-alive',
    }
    return StreamingResponse(generate(), headers=headers)


DEFAULT_ATTRIBUTES = (
    'index',
    'uuid',
    'name',
    'timestamp',
    'memory.total',
    'memory.free',
    'memory.used',
    'utilization.gpu',
    'utilization.memory'
)

@app.get("/stream-nvidia-smi-json", response_class=StreamingResponse)
def stream_nvidia_smi_json(nvidia_smi_path:str='nvidia-smi', no_units:bool=True):    
    keys=DEFAULT_ATTRIBUTES
    nu_opt = '' if not no_units else ',nounits'                
    command = shlex.split('%s -lms 500 --query-gpu=%s --format=csv%s' % (nvidia_smi_path, ','.join(keys), nu_opt))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    def generate():        
        gpus = {}
        try:
            for line in iter(process.stdout.readline, ''):
                # print(line)
                if '[%]' in line:
                    header = [l.strip() for l in line.split(',')]
                    continue            
                line = [l.strip() for l in line.split(', ')]
                # print(line)
                gpu = {k:v for k,v in zip(header,line)}
                # print(gpu)
                gpus[gpu['uuid']]=gpu
                yield f"data: {json.dumps(gpus).encode('utf-8')}\n\n"
        finally:
            process.stdout.close()
            process.wait()

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'text/event-stream',
        'Connection': 'keep-alive',
    }
    return StreamingResponse(generate(), headers=headers)


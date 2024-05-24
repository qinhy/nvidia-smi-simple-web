import re
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
        end_delimiter = "\+-+\+-+\+-+\+\n"
        start_delimiter = "\+-+\+\n[^|]*"
        collecting = False  # This flag indicates if we are between the start and end delimiters

        try:
            # Read each line from the subprocess' stdout
            for line in iter(process.stdout.readline, ''):
                if re.match(start_delimiter, line):
                    collecting = True  # Start collecting lines
                    buffer = line  # Initialize buffer with the start delimiter line
                elif collecting:
                    buffer += line
                    if re.match(end_delimiter, line):
                        collecting = False  # Stop collecting lines
                        # print(buffer)
                        yield f"data: {buffer.encode('utf-8')}\n\n"  # Send the complete block
                        buffer = ""  # Reset buffer for the next block
        finally:
            process.stdout.close()
            process.wait()

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'text/event-stream',
        'Connection': 'keep-alive',
    }
    return StreamingResponse(generate(), headers=headers)

# @app.get("/stream-nvidia-smi")
# def stream_nvidia_smi():
#     # Prepare the command and split it correctly
#     command = shlex.split("nvidia-smi -lms 500")

#     # Start the subprocess with unbuffered output
#     process = subprocess.Popen(
#         command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
#     )

#     def generate():
#         # Output each line from the subprocess' stdout
#         for line in iter(process.stdout.readline, ''):
#             yield line.encode('utf-8')
#         process.stdout.close()
#         process.wait()

#     return StreamingResponse(generate(), media_type="text/plain")

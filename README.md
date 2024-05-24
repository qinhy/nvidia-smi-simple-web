# nvidia-smi-simple-web

### Step 1: Setting Up the FastAPI Backend

1. **Install FastAPI and Uvicorn:**
   You will need `FastAPI` and `Uvicorn` (an ASGI server) to run your API. Install them using pip:

   ```bash
   pip install fastapi uvicorn
   ```

2. **Create a FastAPI App:**
   Create a Python file for your FastAPI application. Here’s a simple example that executes `nvidia-smi` and returns the result:

   ```python
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
   ```

### Step 2: Creating the Frontend

1. **HTML and JavaScript:**
   You can serve a simple HTML page directly from FastAPI or host it separately. Here’s a simple HTML page with JavaScript to fetch and display the data:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>NVIDIA SMI Output</title>
   </head>
   <body>
       <pre id="nvidia-smi-output">Loading...</pre>
       <script>
           async function fetchNvidiaSmi() {
               const response = await fetch('/nvidia-smi');
               const data = await response.json();
               document.getElementById('nvidia-smi-output').textContent = data.data || data.error;
           }
           setInterval(fetchNvidiaSmi, 500);  // Update every 500ms
           fetchNvidiaSmi();  // Initial fetch
       </script>
   </body>
   </html>
   ```

### Step 3: Running the Server

Run your FastAPI application using Uvicorn:

```bash
uvicorn filename:app --reload
```

Replace `filename` with the name of your Python file.

### Step 4: Accessing the Web GUI

Open your browser and go to `http://localhost:8000`. You should see the `nvidia-smi` output being displayed and updated every 500 milliseconds.

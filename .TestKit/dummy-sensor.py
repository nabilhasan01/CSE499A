import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import asyncio

# Initialize FastAPI app
app = FastAPI()

# Set the static file directory (e.g., "Files")
DIRECTORY = "Files"
app.mount("/files", StaticFiles(directory=DIRECTORY), name="files")

# Preset sensor data
presets = [
    {"temperature": 29.49, "humidity": 94.73, "ph": 6.19},
    {"temperature": 26.18, "humidity": 86.52, "ph": 6.26},
    {"temperature": 43.36, "humidity": 93.35, "ph": 6.94},
    {"temperature": 34.28, "humidity": 90.56, "ph": 6.83},
    {"temperature": 22.91, "humidity": 90.70, "ph": 5.60}
]

# Initial sensor data
sensor_data = presets[0]

# Function to update sensor data every 3 seconds
async def update_sensor_data():
    global sensor_data
    while True:
        # Cycle through presets randomly
        sensor_data = random.choice(presets)
        await asyncio.sleep(1)

# Start the background task to update sensor data
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_sensor_data())

# Endpoint to get the current sensor data
@app.get("/sensor-data")
async def get_sensor_data():
    return sensor_data

# Helper function to generate HTML page with file/folder list
def generate_file_list(path: str):
    """Generate an HTML page with clickable links to files and directories."""
    try:
        # List all files and directories
        entries = os.listdir(path)
        links = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                # If it's a directory, link to it
                links.append(f'<li><a href="/{entry}/">{entry}/</a></li>')
            else:
                # If it's a file, link to it
                links.append(f'<li><a href="/files/{entry}">{entry}</a></li>')

        # Return the HTML page with links
        return f"""
            <html>
                <body>
                    <h1>Directory: {path}</h1>
                    <ul>
                        {''.join(links)}
                    </ul>
                </body>
            </html>
        """
    except FileNotFoundError:
        return f"""
            <html>
                <body>
                    <h1>Error: Directory not found</h1>
                </body>
            </html>
        """

# Endpoint to display list of files and folders in the "Files" directory
@app.get("/", response_class=HTMLResponse)
async def list_files():
    return generate_file_list(DIRECTORY)

# Endpoint for browsing into subdirectories
@app.get("/{folder_name}/", response_class=HTMLResponse)
async def list_subfolder_files(folder_name: str):
    folder_path = os.path.join(DIRECTORY, folder_name)
    return generate_file_list(folder_path)

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
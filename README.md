# Golf Quyt Analyzer

Golf Quyt Analyzer is a computer vision application for analyzing golf swing videos. The system lets users upload a swing video, extracts pose data, calculates motion metrics, generates an annotated output video, and predicts the player's handicap band.

## Features

- Upload golf swing videos from a web interface.
- Process videos with a Node.js backend and Python analysis scripts.
- Extract pose landmarks and generate skeleton overlay videos.
- Predict handicap band and return metrics such as swing speed and arm angle.
- Provide model training and preprocessing notebooks/pipelines under the `model` directory.

## Project Structure

```text
.
+-- dataset/                 # Local video dataset, excluded from git
+-- model/                   # Notebooks, pipelines, training outputs, and model assets
+-- website/
|   +-- backend/             # Express API and Python video processing
|   +-- frontend/            # React + Vite web application
+-- README.md
```

## Dataset

The dataset is hosted on Google Drive:

[Download the dataset here](https://drive.google.com/file/d/1An0NDms-Ku354V0mct9fE577wErdFT5I/view?usp=drive_link)

After downloading and extracting the dataset, create `model/Public Test` and copy the dataset contents into that folder:

```text
model/
+-- Public Test/
    +-- Trong nha - Indoor/
    +-- Ngoai troi - Outdoor/
```

The root-level `dataset/` folder can be used to keep a local copy of the dataset. It is ignored by git because the video files are large.

## Requirements

- Node.js 16 or later
- Python 3.8 or later
- FFmpeg installed and available in `PATH`
- pip/virtualenv for Python dependencies

## Installation

### 1. Backend

```bash
cd website/backend
npm install
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Frontend

```bash
cd ../frontend
npm install
```

## Running the Application

Open two separate terminals.

Terminal 1 - backend:

```bash
cd website/backend
npm start
```

The backend runs at `http://localhost:5001`.

Terminal 2 - frontend:

```bash
cd website/frontend
npm run dev
```

The frontend usually runs at `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173` in a browser.
2. Upload a golf swing video.
3. Wait for the backend to process the video.
4. Review the processed video and analysis metrics.

## Development Notes

- The video analysis endpoint is `POST http://127.0.0.1:5001/analyze`.
- Backend inference models are stored in `website/backend/models`.
- The backend requires `website/backend/processed_videos/features/feature_scaler.json`.
- Training and preprocessing code is stored in `model/pipeline` and the notebooks under `model`.
- Do not commit `dataset/`, `node_modules/`, virtual environments, Python caches, temporary uploads, or generated video outputs.

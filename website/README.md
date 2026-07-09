# Golf Quyt Analyzer

> **AI-Powered Golf Swing Analysis Application**
>
> This tool leverages computer vision to analyze golf swings from video uploads, providing detailed metrics like swing speed, arm angle, and handicap band prediction.

---

## Features

- **Automated Swing Detection**: Automatically identifies the swing sequence in a video.
- **Pose Estimation**: Tracks key body joints throughout the swing.
- **Metric Analysis**: Calculates swing speed (m/s) and arm angles.
- **Handicap Prediction**: Uses AI to estimate the player's handicap band.
- **Visual Feedback**: Generates an annotated video with skeleton overlays.

---

## System Requirements

Before running the project, ensure your system meets the following requirements:

- **Node.js**: v16 or higher
- **Python**: v3.8 or higher
- **FFmpeg**: Required for video processing (must be in system PATH)

---

## Installation Guide

Follow these steps to set up the development environment.

### 1. Clone the Repository

```bash
git clone https://github.com/Tienluat123/golfquyt.git
cd golfquyt
```

### 2. Backend Configuration

Navigate to the backend directory and install dependencies.

**Node.js Dependencies:**

```bash
cd backend
npm install
```

**Python Environment:**

It is highly recommended to use a virtual environment to manage Python dependencies.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

> **Note:** Ensure FFmpeg is installed.
>
> - **macOS**: `brew install ffmpeg`
> - **Windows**: Download and add to PATH.

### 3. Frontend Configuration

Navigate to the frontend directory and install dependencies.

```bash
cd ../frontend
npm install
```

---

## Running the Application

To run the full application, you need to start both the backend and frontend servers in separate terminal windows.

### Step 1: Start Backend Server

From the `backend` directory:

```bash
# Ensure your python virtual environment is activated
npm start
```

_Server will start at: `http://localhost:5001`_

### Step 2: Start Frontend Client

From the `frontend` directory:

```bash
npm run dev
```

_Application will be accessible at: `http://localhost:5173`_

---

## Usage Instructions

1.  Open your web browser and navigate to the frontend URL (usually `http://localhost:5173`).
2.  Click the upload area to select a golf swing video from your computer.
3.  Wait for the AI to process the video (this may take a few seconds depending on video length).
4.  Review your analysis results, including the processed video playback and calculated metrics.

---

## Project Structure

- **backend/**: Contains the Node.js server, Python processing scripts, and AI models.
- **frontend/**: Contains the React application and UI components.

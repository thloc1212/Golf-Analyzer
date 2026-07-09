import sys
import os
import json
import subprocess
from pathlib import Path
import traceback

import cv2
import numpy as np
import torch
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import local modules
try:
    import config
    from feature_engineering import FeatureEngineer
    from model_utils import load_model
    from pipeline.types import PoseSequence
    from pose_processing import PoseProcessor
    from video_processing import VideoProcessor
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class GolfPhaseDetector:
    """
    Simple state machine to detect golf swing phases.
    Based on relative positions of wrist, shoulder, and hip.
    """

    def __init__(self):
        self.phase = "Address"
        self.state = 0
        # 0: Address, 1: Takeaway, 2: Backswing, 3: Top,
        # 4: Downswing, 5: Impact, 6: Follow Through, 7: Finish
        self.min_wrist_y = 1.0

    def update(self, landmarks):
        if isinstance(landmarks, list):
            wrist_y = (landmarks[15].y + landmarks[16].y) / 2
            shoulder_y = (landmarks[11].y + landmarks[12].y) / 2
            hip_y = (landmarks[23].y + landmarks[24].y) / 2
        else:
            wrist_y = (landmarks[15, 1] + landmarks[16, 1]) / 2
            shoulder_y = (landmarks[11, 1] + landmarks[12, 1]) / 2
            hip_y = (landmarks[23, 1] + landmarks[24, 1]) / 2

        # Heuristic phase transition
        if self.state == 0:  # Address
            if wrist_y < hip_y:
                self.state = 1
                self.phase = "Takeaway"
        elif self.state == 1:  # Takeaway
            if wrist_y < shoulder_y:
                self.state = 2
                self.phase = "Backswing"
        elif self.state == 2:  # Backswing
            if wrist_y < self.min_wrist_y:
                self.min_wrist_y = wrist_y
            if wrist_y < (shoulder_y - 0.2):
                self.state = 3
                self.phase = "Top"
        elif self.state == 3:  # Top
            if wrist_y > (self.min_wrist_y + 0.05):
                self.state = 4
                self.phase = "Downswing"
        elif self.state == 4:  # Downswing
            if wrist_y > hip_y:
                self.state = 5
                self.phase = "Impact"
        elif self.state == 5:  # Impact
            if wrist_y < shoulder_y:
                self.state = 6
                self.phase = "Follow Through"
        elif self.state == 6:  # Follow Through
            if wrist_y < (shoulder_y - 0.1):
                self.state = 7
                self.phase = "Finish"

        return self.phase


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1], a[0] - b[0]
    )
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle


def draw_landmarks_from_array(rgb_image, landmarks):
    annotated_image = np.copy(rgb_image)
    h, w, _ = annotated_image.shape

    connections = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 7),
        (0, 4),
        (4, 5),
        (5, 6),
        (6, 8),
        (9, 10),
        (11, 12),
        (11, 13),
        (13, 15),
        (15, 17),
        (15, 19),
        (15, 21),
        (17, 19),
        (12, 14),
        (14, 16),
        (16, 18),
        (16, 20),
        (16, 22),
        (18, 20),
        (11, 23),
        (12, 24),
        (23, 24),
        (23, 25),
        (24, 26),
        (25, 27),
        (26, 28),
        (27, 29),
        (28, 30),
        (29, 31),
        (30, 32),
        (27, 31),
        (28, 32),
    ]

    px_landmarks = [(int(lm[0] * w), int(lm[1] * h)) for lm in landmarks]
    joint_colors = [(67, 70, 0)] * len(px_landmarks)

    if len(px_landmarks) > 15:
        left_arm_angle = calculate_angle(
            px_landmarks[11], px_landmarks[13], px_landmarks[15]
        )
        status_color = (0, 255, 0) if left_arm_angle > 160 else (0, 0, 255)
        for idx in [11, 13, 15]:
            joint_colors[idx] = status_color

    if px_landmarks:
        joint_colors[0] = (255, 0, 255)

    for start, end in connections:
        if start < len(px_landmarks) and end < len(px_landmarks):
            cv2.line(
                annotated_image,
                px_landmarks[start],
                px_landmarks[end],
                (96, 188, 249),
                3,
            )

    for i, (px, py) in enumerate(px_landmarks):
        cv2.circle(annotated_image, (px, py), 6, joint_colors[i], -1)
        cv2.circle(annotated_image, (px, py), 2, (255, 255, 255), -1)

    return annotated_image


def process_video(input_path, output_path):
    print(f"Processing video: {input_path}")

    video_processor = VideoProcessor(target_fps=config.TARGET_FPS)
    pose_processor = PoseProcessor()
    feature_engineer = FeatureEngineer()

    model_path = os.path.join("models", "coral_ordinal_model_20260102_001311.pth")
    ai_model = None
    try:
        ai_model = load_model(model_path)
        print("AI Model loaded successfully")
    except Exception as e:
        print(f"Failed to load AI Model: {e}")

    # 1. Load and Resample
    try:
        print("Loading and resampling video...")
        video_clip = video_processor.load_and_resample(Path(input_path))
    except Exception as e:
        print(f"Error loading video: {e}")
        sys.exit(1)

    # 2. Extract Pose
    print("Extracting pose sequence...")
    pose_sequence = pose_processor.extract_sequence(video_clip.frames, video_clip.fps)

    # 3. Detect Swing Window
    print("Detecting swing window...")
    swing_window = video_processor.detect_swing_window(pose_sequence)
    print(f"Swing window: {swing_window.start_frame} - {swing_window.end_frame}")

    # 4. AI Prediction & Metrics
    predicted_band = "Unknown"
    probs_str = ""
    swing_speed_val = 0.0
    arm_angle_val = 0.0

    if ai_model:
        try:
            print("Running AI analysis...")

            start, end = swing_window.start_frame, swing_window.end_frame
            if end - start < 10:
                start, end = 0, len(pose_sequence.data)

            sliced_seq = PoseSequence(
                data=pose_sequence.data[start:end],
                frame_times=pose_sequence.frame_times[start:end],
                fps=pose_sequence.fps,
                interpolation_mask=pose_sequence.interpolation_mask[start:end],
                valid_mask=pose_sequence.valid_mask[start:end],
            )

            # Calculate Metrics (on non-resampled data)
            try:
                metrics_data, _ = pose_processor._interpolate(sliced_seq.data)
                metrics_data = pose_processor._smooth(metrics_data)
                metrics_data = pose_processor._spatial_normalize(metrics_data)

                metrics_seq = PoseSequence(
                    data=metrics_data,
                    frame_times=sliced_seq.frame_times,
                    fps=sliced_seq.fps,
                    interpolation_mask=sliced_seq.interpolation_mask,
                    valid_mask=sliced_seq.valid_mask,
                )

                m_joint_feats, m_global_feats = feature_engineer.compute_features(
                    metrics_seq
                )

                # Swing Speed: Hip Widths/s -> m/s (Approx 1 HW = 0.35m)
                raw_speed = np.percentile(m_global_feats[:, 2], 95)
                swing_speed_val = float(raw_speed * 0.35)

                # Arm Angle
                arm_angle_val = float(np.max(m_joint_feats[:, 13, 12]))

                print(
                    f"Metrics: Speed={swing_speed_val:.2f} m/s, Angle={arm_angle_val:.1f}"
                )

            except Exception as e:
                print(f"Error calculating metrics: {e}")

            # Prepare for AI (Normalize & Resample)
            processed_seq, _ = pose_processor.prepare_sequence(sliced_seq)
            joint_feats, global_feats = feature_engineer.compute_features(processed_seq)

            scaler_path = (
                config.OUTPUT_ROOT
                / config.FINAL_FEATURE_SUBDIR
                / config.SCALER_FILENAME
            )
            if scaler_path.exists():
                try:
                    with open(scaler_path, "r") as f:
                        scaler_data = json.load(f)

                    j_mean = np.array(scaler_data["joint_mean"], dtype=np.float32)
                    j_std = np.array(scaler_data["joint_std"], dtype=np.float32)
                    g_mean = np.array(scaler_data["global_mean"], dtype=np.float32)
                    g_std = np.array(scaler_data["global_std"], dtype=np.float32)

                    j_std[j_std == 0] = 1.0
                    g_std[g_std == 0] = 1.0

                    joint_feats = (joint_feats - j_mean) / j_std
                    global_feats = (global_feats - g_mean) / g_std
                except Exception as e:
                    print(f"Scaler error: {e}")
            else:
                print("Warning: Scaler not found")

            # Inference
            T, J, D = joint_feats.shape
            joint_tensor = torch.from_numpy(joint_feats.reshape(T, J * D)).unsqueeze(0)
            global_tensor = torch.from_numpy(global_feats).unsqueeze(0)

            with torch.no_grad():
                coral_logits, cls_logits = ai_model(joint_tensor, global_tensor)

                probs = torch.softmax(cls_logits, dim=1)
                pred_idx = torch.argmax(probs, dim=1).item()

                predicted_band = config.ID_TO_BAND.get(pred_idx, "Unknown")
                probs_str = str(probs.numpy()[0])

                print(f"AI Result: Band {predicted_band}")

        except Exception as e:
            print(f"AI Prediction Error: {e}")
            traceback.print_exc()

    # 5. Draw Overlay & Export
    print("Generating output video...")
    h, w, _ = video_clip.frames[0].shape
    temp_output = output_path + ".temp.mp4"

    out = cv2.VideoWriter(
        temp_output, cv2.VideoWriter_fourcc(*"mp4v"), video_clip.fps, (w, h)
    )

    phase_detector = GolfPhaseDetector()

    for i, frame in enumerate(video_clip.frames):
        landmarks = pose_sequence.data[i]

        if pose_sequence.valid_mask[i]:
            annotated_frame = draw_landmarks_from_array(frame, landmarks)
            current_phase = phase_detector.update(landmarks)
        else:
            annotated_frame = frame
            current_phase = phase_detector.phase

        cv2.putText(
            annotated_frame,
            f"Phase: {current_phase}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            3,
            cv2.LINE_AA,
        )

        if predicted_band != "Unknown":
            cv2.putText(
                annotated_frame,
                f"Band: {predicted_band}",
                (50, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )

        out.write(annotated_frame)

    out.release()
    pose_processor.reset()

    # 6. Convert to Web Format
    print("Optimizing video for web...")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                temp_output,
                "-vcodec",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "fast",
                output_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if os.path.exists(temp_output):
            os.remove(temp_output)

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg failed or not found, using original output.")
        if os.path.exists(temp_output):
            os.rename(temp_output, output_path)

    print(f"Done! Saved to: {output_path}")

    result = {
        "band": predicted_band,
        "probs": probs_str,
        "swing_start": swing_window.start_frame,
        "swing_end": swing_window.end_frame,
        "swing_speed": swing_speed_val,
        "arm_angle": arm_angle_val,
    }
    print(f"__JSON_START__{json.dumps(result)}__JSON_END__")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_video.py <input> <output>")
        sys.exit(1)

    process_video(sys.argv[1], sys.argv[2])

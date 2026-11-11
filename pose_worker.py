"""Isolated CPU pose inference. Reads TD's downscaled frames; never opens a camera."""
import argparse
import json
import os
from pathlib import Path
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    runtime = root / 'runtime_pose'
    runtime.mkdir(exist_ok=True)
    frame_path = runtime / 'frame.png'
    result_path = runtime / 'pose.json'
    lock_path = runtime / 'worker.pid'
    if lock_path.exists():
        try:
            os.kill(int(lock_path.read_text()), 0)
            return
        except (ValueError, ProcessLookupError, OSError):
            pass
    lock_path.write_text(str(os.getpid()))
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(root/'models/pose_landmarker_lite.task')),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1, min_pose_detection_confidence=.4,
        min_pose_presence_confidence=.4, min_tracking_confidence=.4)
    joints = {11:'shoulder_l',12:'shoulder_r',13:'elbow_l',14:'elbow_r',15:'wrist_l',16:'wrist_r'}
    stamp = 0
    last_input = time.time()
    try:
        with vision.PoseLandmarker.create_from_options(options) as detector:
            while time.time()-last_input < 35:
                try:
                    modified = frame_path.stat().st_mtime_ns
                except FileNotFoundError:
                    time.sleep(.04)
                    continue
                if modified == stamp:
                    time.sleep(.015)
                    continue
                stamp = modified
                last_input = time.time()
                image = cv2.imread(str(frame_path))
                if image is None:
                    continue
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                detected = detector.detect_for_video(image, int(time.monotonic()*1000))
                points = {}
                if detected.pose_landmarks:
                    landmarks = detected.pose_landmarks[0]
                    for index,name in joints.items():
                        p = landmarks[index]
                        confidence = min(p.visibility or 0., p.presence or 0.)
                        if confidence >= .35:
                            points[name] = [float(p.x), float(1.-p.y)]
                payload = {'time':time.time(),'points':points,'pid':os.getpid()}
                temp = result_path.with_suffix('.tmp')
                temp.write_text(json.dumps(payload), encoding='utf-8')
                # Windows readers may briefly hold the old file without delete sharing.
                for attempt in range(5):
                    try:
                        os.replace(temp, result_path)
                        break
                    except PermissionError:
                        time.sleep(.01)
    finally:
        if lock_path.exists() and lock_path.read_text() == str(os.getpid()):
            lock_path.unlink()


if __name__ == '__main__':
    main()

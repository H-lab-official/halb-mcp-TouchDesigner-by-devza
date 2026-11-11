# Third-party components and assets

- MCP Python SDK is installed from PyPI, not vendored in this repository.
- MediaPipe and OpenCV are installed into a separate environment. Their licenses apply to those components.
- The Pose Landmarker Lite model is downloaded directly from Google's MediaPipe model storage; it is not included in Git. Its download URL and SHA256 are recorded by the setup files.
- NVIDIA Video Effects SDK is obtained separately from NVIDIA. No NVIDIA installer, runtime library, or model is redistributed here.
- `assets/landscape_lake.png` was generated with the built-in ImageGen tool. Its generation prompt is recorded in `assets/landscape_generation.txt`.
- No camera frames, personal `.toe` projects, saved credentials, or camera device identifiers are part of the published example.

# Real-Time Offline Android Shoe Recognition App

This is a native Android application in Kotlin that performs real-time shoe recognition using the device camera. The app works completely offline and recognizes registered shoes using an embedding-based approach similar to FaceNet.

## Features
- Completely offline inference using ONNX Runtime.
- Live camera preview via CameraX.
- YOLO based shoe detection and cropping.
- DINOv2 (`dinov2_small_quantized.onnx`) for feature extraction.
- Room database for storing employee details and shoe embeddings.

## Getting Started
1. Open this project in Android Studio.
2. Build and run on a physical device.
3. Use the registration screen to add embeddings for known shoes.
4. The recognition screen will match shoes in real time.

## Architecture
- Kotlin & Coroutines
- MVVM Architecture
- CameraX
- Room Database
- ONNX Runtime Android
- Jetpack Compose
# shoe-recognizer

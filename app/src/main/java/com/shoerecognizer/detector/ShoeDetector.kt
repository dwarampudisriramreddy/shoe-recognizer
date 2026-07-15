package com.shoerecognizer.detector

import android.graphics.Bitmap
import android.graphics.RectF

class ShoeDetector {
    // Stub for YOLO ONNX implementation
    // For now, it returns the whole image as one bounding box, or center crop
    
    fun detect(bitmap: Bitmap): List<RectF> {
        // TODO: Implement actual YOLOv8 inference here.
        // Assuming a dummy detection covering the center of the image.
        val width = bitmap.width.toFloat()
        val height = bitmap.height.toFloat()
        val left = width * 0.1f
        val top = height * 0.1f
        val right = width * 0.9f
        val bottom = height * 0.9f
        return listOf(RectF(left, top, right, bottom))
    }
}

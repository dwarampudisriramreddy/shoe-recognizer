package com.shoerecognizer.camera

import android.graphics.Bitmap
import android.graphics.Matrix
import android.graphics.RectF
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy

class ShoeAnalyzer(
    private val onFrameProcessed: (Bitmap, RectF) -> Unit
) : ImageAnalysis.Analyzer {

    override fun analyze(image: ImageProxy) {
        val bitmap = image.toBitmap()
        
        // Ensure image rotation is handled properly if needed
        val matrix = Matrix()
        matrix.postRotate(image.imageInfo.rotationDegrees.toFloat())
        val rotatedBitmap = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )

        // Fixed rectangle: 60% of width and 60% of height, centered
        val width = rotatedBitmap.width.toFloat()
        val height = rotatedBitmap.height.toFloat()
        val rectWidth = width * 0.6f
        val rectHeight = height * 0.6f
        
        val left = (width - rectWidth) / 2f
        val top = (height - rectHeight) / 2f
        
        val rectF = RectF(left, top, left + rectWidth, top + rectHeight)
        
        // Crop the bitmap
        val croppedBitmap = Bitmap.createBitmap(
            rotatedBitmap,
            left.toInt(),
            top.toInt(),
            rectWidth.toInt(),
            rectHeight.toInt()
        )
        
        // Pass cropped image and the bounding box back
        onFrameProcessed(croppedBitmap, rectF)
        
        image.close()
    }
}

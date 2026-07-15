import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# --- SHOE ANALYZER (Fixed Crop) ---
analyzer_path = os.path.join(base_dir, "camera/ShoeAnalyzer.kt")
with open(analyzer_path, "w") as f:
    f.write("""package com.shoerecognizer.camera

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
""")

# --- VIEWMODEL (Process Crop) ---
vm_path = os.path.join(base_dir, "ui/MainViewModel.kt")
with open(vm_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.app.Application
import android.graphics.Bitmap
import android.graphics.RectF
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.shoerecognizer.embedding.EmbeddingExtractor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val _recognitionState = MutableStateFlow("Please place the shoe inside the rectangle")
    val recognitionState: StateFlow<String> = _recognitionState
    
    private var extractor: EmbeddingExtractor? = null
    
    init {
        // Safe initialization, ignoring missing files during dev
        try {
            extractor = EmbeddingExtractor(application)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    fun processFrame(croppedBitmap: Bitmap, box: RectF) {
        viewModelScope.launch {
            val embedding = extractor?.extract(croppedBitmap)
            if (embedding != null) {
                // Here we would compare against Room DB embeddings using SimilarityUtil
                // For now, update state to show successful extraction
                _recognitionState.value = "Extracted embedding! Comparing..."
            } else {
                _recognitionState.value = "Failed to extract embedding."
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        extractor?.close()
    }
}
""")

print("Updated ShoeAnalyzer and MainViewModel for fixed rectangle logic")

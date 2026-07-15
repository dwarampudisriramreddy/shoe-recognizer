package com.shoerecognizer.ui

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

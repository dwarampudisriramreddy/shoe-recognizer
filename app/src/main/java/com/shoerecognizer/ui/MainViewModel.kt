package com.shoerecognizer.ui

import android.app.Application
import android.graphics.Bitmap
import android.graphics.RectF
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.room.Room
import com.shoerecognizer.database.AppDatabase
import com.shoerecognizer.embedding.EmbeddingExtractor
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.repository.ShoeRepository
import com.shoerecognizer.utils.SimilarityUtil
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val _recognitionState = MutableStateFlow("Please place the shoe inside the rectangle")
    val recognitionState: StateFlow<String> = _recognitionState
    
    private val _shoesList = MutableStateFlow<List<Pair<Shoe, String>>>(emptyList())
    val shoesList: StateFlow<List<Pair<Shoe, String>>> = _shoesList
    
    var lastCroppedBitmap: Bitmap? = null
        private set
    
    private var extractor: EmbeddingExtractor? = null
    private val database = Room.databaseBuilder(
        application,
        AppDatabase::class.java, "shoe-recognizer-db"
    ).build()
    
    private val repository = ShoeRepository(database.shoeDao())
    
    init {
        try {
            extractor = EmbeddingExtractor(application)
        } catch (e: Exception) {
            e.printStackTrace()
        }
        loadShoes()
    }
    
    fun processFrame(croppedBitmap: Bitmap, box: RectF) {
        lastCroppedBitmap = croppedBitmap
        viewModelScope.launch {
            val embedding = extractor?.extract(croppedBitmap)
            if (embedding != null) {
                val allEmbeddings = repository.getAllEmbeddings()
                var bestMatchScore = -1.0f
                var bestMatchShoeId: String? = null
                
                for (storedEmb in allEmbeddings) {
                    val storedVector = SimilarityUtil.parseEmbedding(storedEmb.embeddingVector)
                    val score = SimilarityUtil.cosineSimilarity(embedding, storedVector)
                    if (score > bestMatchScore) {
                        bestMatchScore = score
                        bestMatchShoeId = storedEmb.shoeId
                    }
                }
                
                if (bestMatchScore >= 0.85f && bestMatchShoeId != null) {
                    val shoe = repository.getShoe(bestMatchShoeId)
                    val student = shoe?.studentId?.let { repository.getStudent(it) }
                    
                    if (student != null) {
                        _recognitionState.value = "Student: ${student.studentName} (${(bestMatchScore * 100).toInt()}%)"
                    } else {
                        _recognitionState.value = "Unknown Student"
                    }
                } else {
                    _recognitionState.value = "Unknown Shoe"
                }
            } else {
                _recognitionState.value = "Failed to extract embedding."
            }
        }
    }
    
    fun registerShoe(studentId: String, studentName: String, shoeDesc: String) {
        val bitmapToRegister = lastCroppedBitmap ?: return
        viewModelScope.launch {
            _recognitionState.value = "Registering..."
            val embeddingVector = extractor?.extract(bitmapToRegister)
            if (embeddingVector != null) {
                val std = com.shoerecognizer.models.Student(studentId, studentName)
                val shoeId = java.util.UUID.randomUUID().toString()
                val shoe = com.shoerecognizer.models.Shoe(shoeId, studentId, shoeDesc)
                val embString = SimilarityUtil.formatEmbedding(embeddingVector)
                val emb = com.shoerecognizer.models.Embedding(shoeId = shoeId, embeddingVector = embString, createdDate = System.currentTimeMillis())
                
                try {
                    repository.addStudent(std)
                } catch (e: Exception) {}
                repository.addShoe(shoe)
                repository.addEmbedding(emb)
                _recognitionState.value = "Registered successfully!"
                loadShoes()
            } else {
                _recognitionState.value = "Registration failed."
            }
        }
    }
    
    fun loadShoes() {
        viewModelScope.launch {
            val shoes = repository.getAllShoes()
            val data = shoes.map { shoe ->
                val std = repository.getStudent(shoe.studentId)
                Pair(shoe, std?.studentName ?: "Unknown")
            }
            _shoesList.value = data
        }
    }
    
    fun deleteShoe(shoe: Shoe) {
        viewModelScope.launch {
            repository.deleteShoeAndEmbeddings(shoe)
            loadShoes()
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        extractor?.close()
    }
}

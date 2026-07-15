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
                    val employee = shoe?.employeeId?.let { repository.getEmployee(it) }
                    
                    if (employee != null) {
                        _recognitionState.value = "Employee: ${employee.employeeName} (${(bestMatchScore * 100).toInt()}%)"
                    } else {
                        _recognitionState.value = "Unknown Employee"
                    }
                } else {
                    _recognitionState.value = "Unknown Shoe"
                }
            } else {
                _recognitionState.value = "Failed to extract embedding."
            }
        }
    }
    
    fun registerShoe(employeeId: String, employeeName: String, department: String, shoeDesc: String) {
        val bitmapToRegister = lastCroppedBitmap ?: return
        viewModelScope.launch {
            _recognitionState.value = "Registering..."
            val embeddingVector = extractor?.extract(bitmapToRegister)
            if (embeddingVector != null) {
                val emp = com.shoerecognizer.models.Employee(employeeId, employeeName, department)
                val shoeId = java.util.UUID.randomUUID().toString()
                val shoe = com.shoerecognizer.models.Shoe(shoeId, employeeId, shoeDesc)
                val embString = SimilarityUtil.formatEmbedding(embeddingVector)
                val emb = com.shoerecognizer.models.Embedding(shoeId = shoeId, embeddingVector = embString, createdDate = System.currentTimeMillis())
                
                try {
                    repository.addEmployee(emp)
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
                val emp = repository.getEmployee(shoe.employeeId)
                Pair(shoe, emp?.employeeName ?: "Unknown")
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

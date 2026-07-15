import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer/ui"

vm_path = os.path.join(base_dir, "MainViewModel.kt")
with open(vm_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.app.Application
import android.graphics.Bitmap
import android.graphics.RectF
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.room.Room
import com.shoerecognizer.database.AppDatabase
import com.shoerecognizer.embedding.EmbeddingExtractor
import com.shoerecognizer.repository.ShoeRepository
import com.shoerecognizer.utils.SimilarityUtil
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val _recognitionState = MutableStateFlow("Please place the shoe inside the rectangle")
    val recognitionState: StateFlow<String> = _recognitionState
    
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
    }
    
    fun processFrame(croppedBitmap: Bitmap, box: RectF) {
        // Keep track of the latest crop in case the user wants to register it
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
                } catch (e: Exception) {
                    // Ignore if employee already exists
                }
                repository.addShoe(shoe)
                repository.addEmbedding(emb)
                _recognitionState.value = "Registered successfully!"
            } else {
                _recognitionState.value = "Registration failed."
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        extractor?.close()
    }
}
""")

reg_screen_path = os.path.join(base_dir, "RegistrationScreen.kt")
with open(reg_screen_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.unit.dp

@Composable
fun RegistrationScreen(viewModel: MainViewModel, onNavigateBack: () -> Unit) {
    var employeeId by remember { mutableStateOf("") }
    var employeeName by remember { mutableStateOf("") }
    var department by remember { mutableStateOf("") }
    var shoeDescription by remember { mutableStateOf("") }
    
    val currentImage = viewModel.lastCroppedBitmap

    Column(modifier = Modifier.padding(16.dp)) {
        Text("Register New Shoe", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        
        if (currentImage != null) {
            Image(
                bitmap = currentImage.asImageBitmap(),
                contentDescription = "Shoe to register",
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .background(Color.LightGray)
            )
        } else {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .background(Color.LightGray),
                contentAlignment = Alignment.Center
            ) {
                Text("No shoe image captured. Go back to camera.")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = employeeId,
            onValueChange = { employeeId = it },
            label = { Text("Employee ID") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = employeeName,
            onValueChange = { employeeName = it },
            label = { Text("Employee Name") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = department,
            onValueChange = { department = it },
            label = { Text("Department") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = shoeDescription,
            onValueChange = { shoeDescription = it },
            label = { Text("Shoe Description") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(16.dp))
        
        Button(
            onClick = {
                viewModel.registerShoe(employeeId, employeeName, department, shoeDescription)
                onNavigateBack()
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = currentImage != null && employeeId.isNotBlank() && employeeName.isNotBlank()
        ) {
            Text("Save to Database")
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedButton(
            onClick = onNavigateBack,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Cancel / Go Back")
        }
    }
}
""")

print("Updated MainViewModel and RegistrationScreen to support real-time image capture")

import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# --- 1. Update ShoeDao.kt ---
dao_path = os.path.join(base_dir, "database/ShoeDao.kt")
with open(dao_path, "w") as f:
    f.write("""package com.shoerecognizer.database

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import com.shoerecognizer.models.Employee
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Dao
interface ShoeDao {
    @Insert
    suspend fun insertEmployee(employee: Employee)
    
    @Insert
    suspend fun insertShoe(shoe: Shoe)
    
    @Insert
    suspend fun insertEmbedding(embedding: Embedding)
    
    @Query("SELECT * FROM embeddings")
    suspend fun getAllEmbeddings(): List<Embedding>
    
    @Query("SELECT * FROM shoes")
    suspend fun getAllShoes(): List<Shoe>
    
    @Query("SELECT * FROM shoes WHERE shoeId = :id LIMIT 1")
    suspend fun getShoeById(id: String): Shoe?
    
    @Query("SELECT * FROM employees WHERE employeeId = :id LIMIT 1")
    suspend fun getEmployeeById(id: String): Employee?
    
    @Delete
    suspend fun deleteShoe(shoe: Shoe)
    
    @Query("DELETE FROM embeddings WHERE shoeId = :id")
    suspend fun deleteEmbeddingsForShoe(id: String)
}
""")

# --- 2. Update ShoeRepository.kt ---
repo_path = os.path.join(base_dir, "repository/ShoeRepository.kt")
with open(repo_path, "w") as f:
    f.write("""package com.shoerecognizer.repository

import com.shoerecognizer.database.ShoeDao
import com.shoerecognizer.models.Embedding
import com.shoerecognizer.models.Employee
import com.shoerecognizer.models.Shoe

class ShoeRepository(private val dao: ShoeDao) {
    suspend fun addEmployee(employee: Employee) = dao.insertEmployee(employee)
    suspend fun addShoe(shoe: Shoe) = dao.insertShoe(shoe)
    suspend fun addEmbedding(embedding: Embedding) = dao.insertEmbedding(embedding)
    suspend fun getAllEmbeddings() = dao.getAllEmbeddings()
    suspend fun getAllShoes() = dao.getAllShoes()
    suspend fun getShoe(id: String) = dao.getShoeById(id)
    suspend fun getEmployee(id: String) = dao.getEmployeeById(id)
    
    suspend fun deleteShoeAndEmbeddings(shoe: Shoe) {
        dao.deleteEmbeddingsForShoe(shoe.shoeId)
        dao.deleteShoe(shoe)
    }
}
""")

# --- 3. Update MainViewModel.kt ---
vm_path = os.path.join(base_dir, "ui/MainViewModel.kt")
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
                } catch (e: Exception) {})
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
""")

# --- 4. Update AppNavigation.kt ---
nav_path = os.path.join(base_dir, "ui/AppNavigation.kt")
with open(nav_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

@Composable
fun AppNavigation(viewModel: MainViewModel) {
    var currentScreen by remember { mutableStateOf("camera") }
    
    when (currentScreen) {
        "camera" -> CameraPreviewScreen(
            viewModel = viewModel,
            onNavigateToRegister = { currentScreen = "register" },
            onNavigateToDatabase = { currentScreen = "database" }
        )
        "register" -> RegistrationScreen(
            viewModel = viewModel,
            onNavigateBack = { currentScreen = "camera" }
        )
        "database" -> DatabaseScreen(
            viewModel = viewModel,
            onNavigateBack = { currentScreen = "camera" }
        )
    }
}
""")

# --- 5. Update CameraPreview.kt ---
camera_path = os.path.join(base_dir, "ui/CameraPreview.kt")
with open(camera_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.shoerecognizer.camera.ShoeAnalyzer
import java.util.concurrent.Executors

@Composable
fun CameraPreviewScreen(viewModel: MainViewModel, onNavigateToRegister: () -> Unit, onNavigateToDatabase: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    
    val recognitionText by viewModel.recognitionState.collectAsState()
    
    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                val executor = ContextCompat.getMainExecutor(ctx)
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val imageAnalyzer = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .also {
                            it.setAnalyzer(Executors.newSingleThreadExecutor(), ShoeAnalyzer { croppedBitmap, box ->
                                viewModel.processFrame(croppedBitmap, box)
                            })
                        }
                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(lifecycleOwner, cameraSelector, preview, imageAnalyzer)
                    } catch(exc: Exception) {}
                }, executor)
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )
        
        AndroidView(
            factory = { ctx -> BoundingBoxOverlay(ctx) },
            update = { view -> view.updateText(recognitionText) },
            modifier = Modifier.fillMaxSize()
        )
        
        Row(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(32.dp)
        ) {
            FloatingActionButton(onClick = onNavigateToDatabase, modifier = Modifier.padding(end = 16.dp)) {
                Text("DB", modifier = Modifier.padding(16.dp))
            }
            FloatingActionButton(onClick = onNavigateToRegister) {
                Text("Register", modifier = Modifier.padding(16.dp))
            }
        }
    }
}
""")

# --- 6. Create DatabaseScreen.kt ---
db_screen_path = os.path.join(base_dir, "ui/DatabaseScreen.kt")
with open(db_screen_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun DatabaseScreen(viewModel: MainViewModel, onNavigateBack: () -> Unit) {
    val shoesList by viewModel.shoesList.collectAsState()

    Column(modifier = Modifier.padding(16.dp).fillMaxSize()) {
        Text("Database Records", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        
        if (shoesList.isEmpty()) {
            Text("No shoes registered yet.")
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(shoesList) { pair ->
                    val shoe = pair.first
                    val employeeName = pair.second
                    
                    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                        Row(
                            modifier = Modifier.padding(16.dp).fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Employee: $employeeName")
                                Text("Desc: ${shoe.description}")
                                Text("ID: ${shoe.shoeId.take(8)}...")
                            }
                            Button(onClick = { viewModel.deleteShoe(shoe) }) {
                                Text("Delete")
                            }
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedButton(onClick = onNavigateBack, modifier = Modifier.fillMaxWidth()) {
            Text("Go Back")
        }
    }
}
""")

print("Added full database CRUD screens")

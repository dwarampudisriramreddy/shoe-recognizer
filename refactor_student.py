import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# 1. Models
with open(os.path.join(base_dir, "models/Entities.kt"), "w") as f:
    f.write("""package com.shoerecognizer.models

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "students")
data class Student(
    @PrimaryKey val studentId: String,
    val studentName: String
)

@Entity(tableName = "shoes")
data class Shoe(
    @PrimaryKey val shoeId: String,
    val studentId: String,
    val description: String
)

@Entity(tableName = "embeddings")
data class Embedding(
    @PrimaryKey(autoGenerate = true) val embeddingId: Int = 0,
    val shoeId: String,
    val embeddingVector: String,
    val createdDate: Long
)
""")

# 2. Database
with open(os.path.join(base_dir, "database/AppDatabase.kt"), "w") as f:
    f.write("""package com.shoerecognizer.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.shoerecognizer.models.Student
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Database(entities = [Student::class, Shoe::class, Embedding::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun shoeDao(): ShoeDao
}
""")

# 3. Dao
with open(os.path.join(base_dir, "database/ShoeDao.kt"), "w") as f:
    f.write("""package com.shoerecognizer.database

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import com.shoerecognizer.models.Student
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Dao
interface ShoeDao {
    @Insert
    suspend fun insertStudent(student: Student)
    
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
    
    @Query("SELECT * FROM students WHERE studentId = :id LIMIT 1")
    suspend fun getStudentById(id: String): Student?
    
    @Delete
    suspend fun deleteShoe(shoe: Shoe)
    
    @Query("DELETE FROM embeddings WHERE shoeId = :id")
    suspend fun deleteEmbeddingsForShoe(id: String)
}
""")

# 4. Repository
with open(os.path.join(base_dir, "repository/ShoeRepository.kt"), "w") as f:
    f.write("""package com.shoerecognizer.repository

import com.shoerecognizer.database.ShoeDao
import com.shoerecognizer.models.Embedding
import com.shoerecognizer.models.Student
import com.shoerecognizer.models.Shoe

class ShoeRepository(private val dao: ShoeDao) {
    suspend fun addStudent(student: Student) = dao.insertStudent(student)
    suspend fun addShoe(shoe: Shoe) = dao.insertShoe(shoe)
    suspend fun addEmbedding(embedding: Embedding) = dao.insertEmbedding(embedding)
    suspend fun getAllEmbeddings() = dao.getAllEmbeddings()
    suspend fun getAllShoes() = dao.getAllShoes()
    suspend fun getShoe(id: String) = dao.getShoeById(id)
    suspend fun getStudent(id: String) = dao.getStudentById(id)
    
    suspend fun deleteShoeAndEmbeddings(shoe: Shoe) {
        dao.deleteEmbeddingsForShoe(shoe.shoeId)
        dao.deleteShoe(shoe)
    }
}
""")

# 5. MainViewModel
with open(os.path.join(base_dir, "ui/MainViewModel.kt"), "w") as f:
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
""")

# 6. RegistrationScreen
with open(os.path.join(base_dir, "ui/RegistrationScreen.kt"), "w") as f:
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
    var studentId by remember { mutableStateOf("") }
    var studentName by remember { mutableStateOf("") }
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
            value = studentId,
            onValueChange = { studentId = it },
            label = { Text("Student ID") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = studentName,
            onValueChange = { studentName = it },
            label = { Text("Student Name") },
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
                viewModel.registerShoe(studentId, studentName, shoeDescription)
                onNavigateBack()
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = currentImage != null && studentId.isNotBlank() && studentName.isNotBlank()
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

# 7. DatabaseScreen
with open(os.path.join(base_dir, "ui/DatabaseScreen.kt"), "w") as f:
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
                    val studentName = pair.second
                    
                    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                        Row(
                            modifier = Modifier.padding(16.dp).fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Student: $studentName")
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

print("Refactored Employee to Student and removed Department")

import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"
os.makedirs(base_dir, exist_ok=True)

directories = [
    "ui",
    "camera",
    "detector",
    "embedding",
    "recognition",
    "database",
    "repository",
    "models",
    "utils",
    "ui/theme"
]

for d in directories:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

# Database
with open(os.path.join(base_dir, "database/AppDatabase.kt"), "w") as f:
    f.write("""package com.shoerecognizer.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.shoerecognizer.models.Employee
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Database(entities = [Employee::class, Shoe::class, Embedding::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun shoeDao(): ShoeDao
}
""")

with open(os.path.join(base_dir, "database/ShoeDao.kt"), "w") as f:
    f.write("""package com.shoerecognizer.database

import androidx.room.Dao
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
    
    @Query("SELECT * FROM shoes WHERE shoeId = :id LIMIT 1")
    suspend fun getShoeById(id: String): Shoe?
    
    @Query("SELECT * FROM employees WHERE employeeId = :id LIMIT 1")
    suspend fun getEmployeeById(id: String): Employee?
}
""")

# Models
with open(os.path.join(base_dir, "models/Entities.kt"), "w") as f:
    f.write("""package com.shoerecognizer.models

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "employees")
data class Employee(
    @PrimaryKey val employeeId: String,
    val employeeName: String,
    val department: String
)

@Entity(tableName = "shoes")
data class Shoe(
    @PrimaryKey val shoeId: String,
    val employeeId: String,
    val description: String
)

@Entity(tableName = "embeddings")
data class Embedding(
    @PrimaryKey(autoGenerate = true) val embeddingId: Int = 0,
    val shoeId: String,
    val embeddingVector: String, // Stored as JSON or comma-separated string for simplicity
    val createdDate: Long
)
""")

# MainActivity
with open(os.path.join(base_dir, "ui/MainActivity.kt"), "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import com.shoerecognizer.ui.theme.ShoeRecognizerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ShoeRecognizerTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    Text("Real-Time Offline Android Shoe Recognition App")
}
""")

# Theme
with open(os.path.join(base_dir, "ui/theme/Theme.kt"), "w") as f:
    f.write("""package com.shoerecognizer.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

@Composable
fun ShoeRecognizerTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = lightColorScheme(),
        content = content
    )
}
""")

# Repository
with open(os.path.join(base_dir, "repository/ShoeRepository.kt"), "w") as f:
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
    suspend fun getShoe(id: String) = dao.getShoeById(id)
    suspend fun getEmployee(id: String) = dao.getEmployeeById(id)
}
""")

print("Scaffolded Kotlin files")

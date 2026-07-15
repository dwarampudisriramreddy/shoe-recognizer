package com.shoerecognizer.database

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

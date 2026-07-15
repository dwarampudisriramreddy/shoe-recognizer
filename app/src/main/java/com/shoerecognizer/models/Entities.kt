package com.shoerecognizer.models

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

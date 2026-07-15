package com.shoerecognizer.models

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

package com.shoerecognizer.repository

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

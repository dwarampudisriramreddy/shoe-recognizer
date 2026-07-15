package com.shoerecognizer.repository

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

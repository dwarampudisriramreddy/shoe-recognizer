package com.shoerecognizer.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.shoerecognizer.models.Employee
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Database(entities = [Employee::class, Shoe::class, Embedding::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun shoeDao(): ShoeDao
}

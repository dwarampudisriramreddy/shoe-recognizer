package com.shoerecognizer.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.shoerecognizer.models.Student
import com.shoerecognizer.models.Shoe
import com.shoerecognizer.models.Embedding

@Database(entities = [Student::class, Shoe::class, Embedding::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun shoeDao(): ShoeDao
}

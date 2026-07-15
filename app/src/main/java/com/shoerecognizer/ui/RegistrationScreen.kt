package com.shoerecognizer.ui

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

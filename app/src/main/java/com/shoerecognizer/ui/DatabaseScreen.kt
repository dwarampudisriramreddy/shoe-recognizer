package com.shoerecognizer.ui

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
                    val employeeName = pair.second
                    
                    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                        Row(
                            modifier = Modifier.padding(16.dp).fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Employee: $employeeName")
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

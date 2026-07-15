package com.shoerecognizer.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

// Simple custom navigation for simplicity instead of adding Navigation Compose dependency
@Composable
fun AppNavigation(viewModel: MainViewModel) {
    var currentScreen by remember { mutableStateOf("camera") }
    
    when (currentScreen) {
        "camera" -> CameraPreviewScreen(
            viewModel = viewModel,
            onNavigateToRegister = { currentScreen = "register" }
        )
        "register" -> RegistrationScreen(
            viewModel = viewModel,
            onNavigateBack = { currentScreen = "camera" }
        )
    }
}

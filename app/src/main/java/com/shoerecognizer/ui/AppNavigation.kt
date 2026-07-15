package com.shoerecognizer.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

@Composable
fun AppNavigation(viewModel: MainViewModel) {
    var currentScreen by remember { mutableStateOf("camera") }
    
    when (currentScreen) {
        "camera" -> CameraPreviewScreen(
            viewModel = viewModel,
            onNavigateToRegister = { currentScreen = "register" },
            onNavigateToDatabase = { currentScreen = "database" }
        )
        "register" -> RegistrationScreen(
            viewModel = viewModel,
            onNavigateBack = { currentScreen = "camera" }
        )
        "database" -> DatabaseScreen(
            viewModel = viewModel,
            onNavigateBack = { currentScreen = "camera" }
        )
    }
}

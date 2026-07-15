import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer/ui"

main_activity_path = os.path.join(base_dir, "MainActivity.kt")
with open(main_activity_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.shoerecognizer.ui.theme.ShoeRecognizerTheme

class MainActivity : ComponentActivity() {
    
    private val viewModel: MainViewModel by viewModels()
    private var hasCameraPermission by mutableStateOf(false)

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        hasCameraPermission = isGranted
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        checkCameraPermission()
        
        setContent {
            ShoeRecognizerTheme {
                if (hasCameraPermission) {
                    AppNavigation(viewModel)
                } else {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("Camera permission is required.")
                    }
                }
            }
        }
    }
    
    private fun checkCameraPermission() {
        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                hasCameraPermission = true
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }
}
""")

app_navigation_path = os.path.join(base_dir, "AppNavigation.kt")
with open(app_navigation_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

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
""")

camera_preview_path = os.path.join(base_dir, "CameraPreview.kt")
with open(camera_preview_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.shoerecognizer.camera.ShoeAnalyzer
import java.util.concurrent.Executors

@Composable
fun CameraPreviewScreen(viewModel: MainViewModel, onNavigateToRegister: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    
    val recognitionText by viewModel.recognitionState.collectAsState()
    
    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                val executor = ContextCompat.getMainExecutor(ctx)
                
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    
                    val imageAnalyzer = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .also {
                            it.setAnalyzer(Executors.newSingleThreadExecutor(), ShoeAnalyzer { croppedBitmap, box ->
                                viewModel.processFrame(croppedBitmap, box)
                            })
                        }
                    
                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                    
                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            cameraSelector,
                            preview,
                            imageAnalyzer
                        )
                    } catch(exc: Exception) {
                        exc.printStackTrace()
                    }
                    
                }, executor)
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )
        
        AndroidView(
            factory = { ctx -> BoundingBoxOverlay(ctx) },
            update = { view ->
                view.updateText(recognitionText)
            },
            modifier = Modifier.fillMaxSize()
        )
        
        FloatingActionButton(
            onClick = onNavigateToRegister,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(32.dp)
        ) {
            Text("Register", modifier = Modifier.padding(16.dp))
        }
    }
}
""")

registration_screen_path = os.path.join(base_dir, "RegistrationScreen.kt")
with open(registration_screen_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun RegistrationScreen(viewModel: MainViewModel, onNavigateBack: () -> Unit) {
    var employeeId by remember { mutableStateOf("") }
    var employeeName by remember { mutableStateOf("") }
    var department by remember { mutableStateOf("") }
    var shoeDescription by remember { mutableStateOf("") }

    Column(modifier = Modifier.padding(16.dp)) {
        Text("Register New Shoe", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = employeeId,
            onValueChange = { employeeId = it },
            label = { Text("Employee ID") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = employeeName,
            onValueChange = { employeeName = it },
            label = { Text("Employee Name") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = department,
            onValueChange = { department = it },
            label = { Text("Department") },
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
                // For simplicity, we are simulating taking a photo by using a dummy feature or returning to camera
                onNavigateBack()
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Cancel / Go Back")
        }
    }
}
""")

print("Updated navigation layout")

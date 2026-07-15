import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# --- VIEWMODEL ---
vm_path = os.path.join(base_dir, "ui/MainViewModel.kt")
with open(vm_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.app.Application
import android.graphics.Bitmap
import android.graphics.RectF
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.shoerecognizer.database.AppDatabase
import com.shoerecognizer.embedding.EmbeddingExtractor
import com.shoerecognizer.repository.ShoeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    // In a real app we would use a DI framework like Hilt
    // Here we initialize manually for simplicity
    
    // We would initialize the database, repository and extractor here
    private val _recognitionState = MutableStateFlow("Initializing...")
    val recognitionState: StateFlow<String> = _recognitionState
    
    fun processFrame(bitmap: Bitmap, boundingBoxes: List<RectF>) {
        // Implement inference and matching logic here
        viewModelScope.launch {
            _recognitionState.value = "Analyzing ${boundingBoxes.size} objects..."
            // Crop bitmap -> extract embedding -> compare -> update state
        }
    }
}
""")

# --- COMPOSE CAMERA UI ---
camera_ui_path = os.path.join(base_dir, "ui/CameraPreview.kt")
with open(camera_ui_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.shoerecognizer.camera.ShoeAnalyzer
import java.util.concurrent.Executors

@Composable
fun CameraPreviewScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    
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
                        it.setAnalyzer(Executors.newSingleThreadExecutor(), ShoeAnalyzer { bitmap, boxes ->
                            viewModel.processFrame(bitmap, boxes)
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
}
""")

print("Scaffolded UI and ViewModels")

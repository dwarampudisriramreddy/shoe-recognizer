import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

camera_ui_path = os.path.join(base_dir, "ui/CameraPreview.kt")
with open(camera_ui_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Box
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
import android.graphics.RectF

@Composable
fun CameraPreviewScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    
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
                                // We could update an overlay view here with the box
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
        
        // Add overlay drawing the fixed rectangle and recognition text
        AndroidView(
            factory = { ctx ->
                BoundingBoxOverlay(ctx).apply {
                    // Update periodically if needed
                }
            },
            modifier = Modifier.fillMaxSize()
        )
    }
}
""")

overlay_ui_path = os.path.join(base_dir, "ui/BoundingBoxOverlay.kt")
with open(overlay_ui_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View

class BoundingBoxOverlay @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val boxPaint = Paint().apply {
        color = Color.GREEN
        style = Paint.Style.STROKE
        strokeWidth = 8f
    }
    
    private val textPaint = Paint().apply {
        color = Color.WHITE
        textSize = 54f
        style = Paint.Style.FILL
        setShadowLayer(4f, 0f, 0f, Color.BLACK)
    }
    
    private var recognitionText: String = "Place shoe inside box"

    fun updateText(text: String) {
        recognitionText = text
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        val width = width.toFloat()
        val height = height.toFloat()
        val rectWidth = width * 0.6f
        val rectHeight = height * 0.6f
        
        val left = (width - rectWidth) / 2f
        val top = (height - rectHeight) / 2f
        val right = left + rectWidth
        val bottom = top + rectHeight
        
        val fixedBox = RectF(left, top, right, bottom)
        
        canvas.drawRect(fixedBox, boxPaint)
        canvas.drawText(recognitionText, fixedBox.left, fixedBox.top - 20f, textPaint)
    }
}
""")

print("Updated CameraPreview and BoundingBoxOverlay for fixed rectangle logic")

import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# --- REGISTRATION SCREEN ---
reg_ui_path = os.path.join(base_dir, "ui/RegistrationScreen.kt")
with open(reg_ui_path, "w") as f:
    f.write("""package com.shoerecognizer.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun RegistrationScreen(viewModel: MainViewModel) {
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
                // Trigger camera capture to crop and embed
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Capture Shoe Images")
        }
    }
}
""")

# --- OVERLAY VIEW ---
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

    private val boxes = mutableListOf<RectF>()
    private val boxPaint = Paint().apply {
        color = Color.RED
        style = Paint.Style.STROKE
        strokeWidth = 8f
    }
    
    private val textPaint = Paint().apply {
        color = Color.WHITE
        textSize = 48f
        style = Paint.Style.FILL
        setShadowLayer(4f, 0f, 0f, Color.BLACK)
    }
    
    private var recognitionText: String = ""

    fun updateBoxes(newBoxes: List<RectF>, text: String) {
        boxes.clear()
        boxes.addAll(newBoxes)
        recognitionText = text
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        for (box in boxes) {
            canvas.drawRect(box, boxPaint)
            if (recognitionText.isNotEmpty()) {
                canvas.drawText(recognitionText, box.left, box.top - 10f, textPaint)
            }
        }
    }
}
""")

print("Scaffolded RegistrationScreen and BoundingBoxOverlay")

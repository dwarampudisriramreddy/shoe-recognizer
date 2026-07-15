import os

base_dir = "/home/sri/shoe-recognizer/app/src/main/java/com/shoerecognizer"

# --- ONNX INFERENCE (Embedding Extractor) ---
embedding_path = os.path.join(base_dir, "embedding/EmbeddingExtractor.kt")
with open(embedding_path, "w") as f:
    f.write("""package com.shoerecognizer.embedding

import android.content.Context
import android.graphics.Bitmap
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.nio.FloatBuffer
import java.util.Collections

class EmbeddingExtractor(context: Context) {
    private val ortEnvironment = OrtEnvironment.getEnvironment()
    private var ortSession: OrtSession? = null

    init {
        val modelBytes = context.assets.open("dinov2_small_model_quantized.onnx").readBytes()
        val sessionOptions = OrtSession.SessionOptions()
        ortSession = ortEnvironment.createSession(modelBytes, sessionOptions)
    }

    fun extract(bitmap: Bitmap): FloatArray? {
        val session = ortSession ?: return null
        val resized = Bitmap.createScaledBitmap(bitmap, 224, 224, true)
        
        // Convert to FloatBuffer [1, 3, 224, 224]
        val floatBuffer = FloatBuffer.allocate(1 * 3 * 224 * 224)
        val pixels = IntArray(224 * 224)
        resized.getPixels(pixels, 0, 224, 0, 0, 224, 224)
        
        // Normalize (ImageNet mean and std)
        val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
        val std = floatArrayOf(0.229f, 0.224f, 0.225f)
        
        for (c in 0..2) {
            for (i in pixels.indices) {
                val pixel = pixels[i]
                val value = when(c) {
                    0 -> ((pixel shr 16) and 0xFF) / 255.0f
                    1 -> ((pixel shr 8) and 0xFF) / 255.0f
                    2 -> (pixel and 0xFF) / 255.0f
                    else -> 0f
                }
                floatBuffer.put(c * 224 * 224 + i, (value - mean[c]) / std[c])
            }
        }
        
        val inputName = session.inputNames.iterator().next()
        val shape = longArrayOf(1, 3, 224, 224)
        floatBuffer.rewind()
        
        val tensor = OnnxTensor.createTensor(ortEnvironment, floatBuffer, shape)
        val result = session.run(Collections.singletonMap(inputName, tensor))
        
        val output = result[0].value as Array<FloatArray>
        return output[0]
    }
    
    fun close() {
        ortSession?.close()
        ortEnvironment.close()
    }
}
""")

# --- ONNX INFERENCE (Shoe Detector) ---
detector_path = os.path.join(base_dir, "detector/ShoeDetector.kt")
with open(detector_path, "w") as f:
    f.write("""package com.shoerecognizer.detector

import android.graphics.Bitmap
import android.graphics.RectF

class ShoeDetector {
    // Stub for YOLO ONNX implementation
    // For now, it returns the whole image as one bounding box, or center crop
    
    fun detect(bitmap: Bitmap): List<RectF> {
        // TODO: Implement actual YOLOv8 inference here.
        // Assuming a dummy detection covering the center of the image.
        val width = bitmap.width.toFloat()
        val height = bitmap.height.toFloat()
        val left = width * 0.1f
        val top = height * 0.1f
        val right = width * 0.9f
        val bottom = height * 0.9f
        return listOf(RectF(left, top, right, bottom))
    }
}
""")

# --- UTILS (Similarity) ---
utils_path = os.path.join(base_dir, "utils/SimilarityUtil.kt")
with open(utils_path, "w") as f:
    f.write("""package com.shoerecognizer.utils

import kotlin.math.sqrt

object SimilarityUtil {
    fun cosineSimilarity(v1: FloatArray, v2: FloatArray): Float {
        var dotProduct = 0.0f
        var norm1 = 0.0f
        var norm2 = 0.0f
        for (i in v1.indices) {
            dotProduct += v1[i] * v2[i]
            norm1 += v1[i] * v1[i]
            norm2 += v2[i] * v2[i]
        }
        if (norm1 == 0.0f || norm2 == 0.0f) return 0.0f
        return (dotProduct / (sqrt(norm1) * sqrt(norm2)))
    }
    
    fun parseEmbedding(embeddingString: String): FloatArray {
        return embeddingString.split(",").map { it.toFloat() }.toFloatArray()
    }
    
    fun formatEmbedding(embedding: FloatArray): String {
        return embedding.joinToString(",")
    }
}
""")

# --- CAMERAX (Frame Analyzer) ---
analyzer_path = os.path.join(base_dir, "camera/ShoeAnalyzer.kt")
with open(analyzer_path, "w") as f:
    f.write("""package com.shoerecognizer.camera

import android.graphics.Bitmap
import android.graphics.RectF
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy

class ShoeAnalyzer(
    private val onFrameProcessed: (Bitmap, List<RectF>) -> Unit
) : ImageAnalysis.Analyzer {

    override fun analyze(image: ImageProxy) {
        val bitmap = image.toBitmap()
        // Dummy detections
        val width = bitmap.width.toFloat()
        val height = bitmap.height.toFloat()
        val boxes = listOf(RectF(width * 0.1f, height * 0.1f, width * 0.9f, height * 0.9f))
        
        onFrameProcessed(bitmap, boxes)
        image.close()
    }
}
""")

print("Scaffolded ONNX wrappers and Camera components")

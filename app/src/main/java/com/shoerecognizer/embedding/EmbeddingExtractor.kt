package com.shoerecognizer.embedding

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

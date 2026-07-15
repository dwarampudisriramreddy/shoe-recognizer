package com.shoerecognizer.utils

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

package com.shoerecognizer.ui

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

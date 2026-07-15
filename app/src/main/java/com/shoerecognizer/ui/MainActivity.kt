package com.shoerecognizer.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import com.shoerecognizer.ui.theme.ShoeRecognizerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ShoeRecognizerTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    Text("Real-Time Offline Android Shoe Recognition App")
}

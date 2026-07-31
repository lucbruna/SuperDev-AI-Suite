package com.superdev.ai.mobile.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun DashboardScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "SuperDev AI Dashboard",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(16.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Edge AI Status", style = MaterialTheme.typography.titleMedium)
                Text(text = "Models Loaded: 3")
                Text(text = "Inference Latency: 12ms")
                Text(text = "Offline Mode: Ready")
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Device Status", style = MaterialTheme.typography.titleMedium)
                Text(text = "Battery: 85%")
                Text(text = "Storage: 2.1 GB used")
                Text(text = "Network: Connected")
            }
        }
    }
}

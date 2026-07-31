package com.superdev.ai.mobile.tests

import org.junit.Test
import org.junit.Assert.*

class EdgeAIEngineTest {
    @Test
    fun testModelLoad() {
        val engine = com.superdev.ai.mobile.ai.EdgeAIEngine()
        assertTrue(engine.loadModel("model.tflite"))
        assertTrue(engine.isModelLoaded())
    }

    @Test
    fun testInferenceWithoutModel() {
        val engine = com.superdev.ai.mobile.ai.EdgeAIEngine()
        val result = engine.runInference("test input")
        assertTrue(result.contains("Error"))
    }

    @Test
    fun testUnloadModel() {
        val engine = com.superdev.ai.mobile.ai.EdgeAIEngine()
        engine.loadModel("model.tflite")
        assertTrue(engine.unloadModel())
        assertFalse(engine.isModelLoaded())
    }
}

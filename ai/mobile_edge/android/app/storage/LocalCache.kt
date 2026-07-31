package com.superdev.ai.mobile.storage

import android.content.Context
import android.content.SharedPreferences

class LocalCache(private val context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("superdev_cache", Context.MODE_PRIVATE)

    fun put(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    fun get(key: String): String? = prefs.getString(key, null)

    fun remove(key: String) {
        prefs.edit().remove(key).apply()
    }

    fun clear() {
        prefs.edit().clear().apply()
    }

    fun contains(key: String): Boolean = prefs.contains(key)
}

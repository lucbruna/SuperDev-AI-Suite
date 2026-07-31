import Foundation

struct DeviceInfo: Codable {
    let id: String
    let name: String
    let platform: String
    let osVersion: String
}

struct SyncConfig: Codable {
    let strategy: String
    let interval: Int
    let wifiOnly: Bool
}

struct OfflineConfig: Codable {
    let enabled: Bool
    let cacheSizeMB: Int
    let maxOfflineDays: Int
}

struct ModelInfo: Codable {
    let modelId: String
    let name: String
    let version: String
    let sizeMB: Double
    let loaded: Bool
}

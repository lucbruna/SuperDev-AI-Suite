import SwiftUI

struct DashboardView: View {
    @State private var modelCount = 3
    @State private var latency = "12ms"
    @State private var batteryLevel = 85

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Edge AI Dashboard")
                .font(.title2)
                .fontWeight(.bold)

            GroupBox("AI Status") {
                LabeledContent("Models Loaded", value: "\(modelCount)")
                LabeledContent("Inference Latency", value: latency)
                LabeledContent("Offline Mode", value: "Ready")
            }

            GroupBox("Device Status") {
                LabeledContent("Battery", value: "\(batteryLevel)%")
                LabeledContent("Storage", value: "2.1 GB used")
                LabeledContent("Network", value: "Connected")
            }
        }
        .padding()
        .navigationTitle("Dashboard")
    }
}

struct ModelsView: View {
    var body: some View {
        List {
            Text("Local NLP Model v2.1")
            Text("Image Classifier v1.5")
            Text("Speech Recognizer v1.0")
        }
        .navigationTitle("Models")
    }
}

struct InferenceView: View {
    @State private var input = ""
    @State private var output = ""

    var body: some View {
        VStack {
            TextField("Enter input...", text: $input)
                .textFieldStyle(.roundedBorder)
            Button("Run Inference") { output = "Result for: \(input)" }
            Text(output).foregroundColor(.secondary)
        }
        .padding()
        .navigationTitle("Inference")
    }
}

struct CacheView: View {
    var body: some View {
        List {
            Text("Cached Items: 42")
            Text("Cache Size: 128 MB")
            Text("Max Cache: 500 MB")
        }
        .navigationTitle("Cache")
    }
}

struct SyncQueueView: View {
    var body: some View {
        List {
            Text("Pending: 5 items")
            Text("Synced: 120 items")
            Text("Failed: 2 items")
        }
        .navigationTitle("Sync Queue")
    }
}

struct BiometricsView: View {
    var body: some View {
        List {
            Text("Face ID: Enabled")
            Text("Touch ID: Enabled")
            Text("Last Auth: 2 min ago")
        }
        .navigationTitle("Biometrics")
    }
}

struct DeviceInfoView: View {
    var body: some View {
        List {
            Text("Platform: iOS 17.0")
            Text("Model: iPhone 15 Pro")
            Text("Security: Enrolled")
        }
        .navigationTitle("Device Info")
    }
}

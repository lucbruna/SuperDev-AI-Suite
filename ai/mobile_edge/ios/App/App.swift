import SwiftUI

@main
struct SuperDevAIApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        NavigationView {
            List {
                Section("Edge AI") {
                    NavigationLink("Dashboard", destination: DashboardView())
                    NavigationLink("Models", destination: ModelsView())
                    NavigationLink("Inference", destination: InferenceView())
                }
                Section("Offline") {
                    NavigationLink("Cache", destination: CacheView())
                    NavigationLink("Sync Queue", destination: SyncQueueView())
                }
                Section("Security") {
                    NavigationLink("Biometrics", destination: BiometricsView())
                    NavigationLink("Device Info", destination: DeviceInfoView())
                }
            }
            .navigationTitle("SuperDev AI")
        }
    }
}

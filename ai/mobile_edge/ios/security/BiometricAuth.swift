import Foundation
import LocalAuthentication

class BiometricAuth {
    func authenticate(reason: String, completion: @escaping (Bool, Error?) -> Void) {
        let context = LAContext()
        var error: NSError?
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
                DispatchQueue.main.async { completion(success, error) }
            }
        } else {
            completion(false, error)
        }
    }

    func biometricType() -> String {
        let context = LAContext()
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else { return "none" }
        switch context.biometryType {
        case .faceID: return "face"
        case .touchID: return "fingerprint"
        case .opticID: return "iris"
        @unknown default: return "unknown"
        }
    }
}

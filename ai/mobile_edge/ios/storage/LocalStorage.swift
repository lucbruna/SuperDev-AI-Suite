import Foundation

class LocalStorage {
    private let defaults = UserDefaults.standard

    func save(key: String, value: Any) {
        defaults.set(value, forKey: key)
    }

    func load(key: String) -> Any? {
        defaults.object(forKey: key)
    }

    func remove(key: String) {
        defaults.removeObject(forKey: key)
    }

    func clear() {
        let dictionary = defaults.dictionaryRepresentation()
        dictionary.keys.forEach { defaults.removeObject(forKey: $0) }
    }
}

import XCTest
@testable import SuperDevAI

class EdgeAITests: XCTestCase {
    func testModelLoad() {
        let engine = EdgeAIService()
        XCTAssertTrue(engine.loadModel(path: "model.mlmodel"))
        XCTAssertTrue(engine.isModelLoaded())
    }

    func testInferenceWithoutModel() {
        let engine = EdgeAIService()
        let result = engine.runInference(input: "test")
        XCTAssertTrue(result.contains("Error"))
    }

    func testUnloadModel() {
        let engine = EdgeAIService()
        engine.loadModel(path: "model.mlmodel")
        XCTAssertTrue(engine.unloadModel())
        XCTAssertFalse(engine.isModelLoaded())
    }
}

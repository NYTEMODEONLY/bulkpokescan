import Foundation

struct ScannedCode: Codable, Identifiable, Hashable {
    enum Source: String, Codable { case scan, manual }

    let value: String
    let source: Source
    let capturedAt: Date

    var id: String { value }
}

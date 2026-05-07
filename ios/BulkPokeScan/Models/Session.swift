import Foundation

@MainActor
final class Session: ObservableObject {
    @Published private(set) var codes: [ScannedCode] = []
    private var undoStack: [[ScannedCode]] = []
    private let undoLimit = 50

    var count: Int { codes.count }

    func contains(_ value: String) -> Bool {
        codes.contains(where: { $0.value == value })
    }

    @discardableResult
    func add(_ value: String, source: ScannedCode.Source) -> Bool {
        guard !value.isEmpty, !contains(value) else { return false }
        snapshot()
        codes.append(ScannedCode(value: value, source: source, capturedAt: Date()))
        return true
    }

    func remove(_ value: String) {
        guard contains(value) else { return }
        snapshot()
        codes.removeAll(where: { $0.value == value })
    }

    func removeAll() {
        guard !codes.isEmpty else { return }
        snapshot()
        codes.removeAll()
    }

    func undo() {
        guard let prev = undoStack.popLast() else { return }
        codes = prev
    }

    /// Block-grouped view: indices `[0..<10, 10..<20, ...]` plus the partial tail.
    func blocks(of size: Int = 10) -> [[ScannedCode]] {
        guard !codes.isEmpty else { return [] }
        return stride(from: 0, to: codes.count, by: size).map {
            Array(codes[$0..<min($0 + size, codes.count)])
        }
    }

    /// Replace contents (used by SessionStore on launch). Does not push undo.
    func replaceAll(_ new: [ScannedCode]) {
        codes = new
        undoStack.removeAll()
    }

    private func snapshot() {
        undoStack.append(codes)
        if undoStack.count > undoLimit { undoStack.removeFirst() }
    }
}

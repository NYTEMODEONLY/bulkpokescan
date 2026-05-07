import SwiftUI
import UIKit

struct ExportSheet: View {
    @EnvironmentObject var session: Session
    @Environment(\.dismiss) var dismiss
    @State private var format: Format = .numbered
    @State private var didCopy = false
    /// Captured once on appear so filename and header timestamps stay stable
    /// for the lifetime of the sheet.
    @State private var exportDate = Date()

    enum Format: String, CaseIterable, Identifiable {
        case numbered    = "Numbered List"
        case raw         = "Raw (one per line)"
        case spaced      = "Space-separated"
        case commad      = "Comma-separated"
        var id: String { rawValue }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("Format", selection: $format) {
                    ForEach(Format.allCases) { f in
                        Text(f.rawValue).tag(f)
                    }
                }
                .pickerStyle(.menu)
                .padding(.horizontal, 16).padding(.top, 12)

                ScrollView {
                    Text(rendered)
                        .font(Typography.mono(12))
                        .foregroundStyle(Palette.text)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(14)
                        .textSelection(.enabled)
                }
                .background(RoundedRectangle(cornerRadius: 12).fill(Palette.input))
                .padding(16)

                if !session.codes.isEmpty, let url = fileURL {
                    HStack(spacing: 10) {
                        copyButton
                        ShareLink(item: url,
                                  subject: Text(shareSubject),
                                  preview: SharePreview(filename)) {
                            Label("Share", systemImage: "square.and.arrow.up")
                                .font(Typography.body(15, weight: .semibold))
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(RoundedRectangle(cornerRadius: 12).fill(Palette.red))
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 16)
                }
            }
            .background(Palette.bg)
            .navigationTitle("Export")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
            .onAppear { exportDate = Date() }
        }
    }

    private var copyButton: some View {
        Button {
            UIPasteboard.general.string = rendered
            HapticsManager.capture()
            withAnimation(.easeOut(duration: 0.15)) { didCopy = true }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
                withAnimation(.easeOut(duration: 0.2)) { didCopy = false }
            }
        } label: {
            Label(didCopy ? "Copied" : "Copy",
                  systemImage: didCopy ? "checkmark" : "doc.on.doc")
                .font(Typography.body(15, weight: .semibold))
                .foregroundStyle(didCopy ? Palette.yellow : Palette.text)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(RoundedRectangle(cornerRadius: 12).fill(Palette.surface2))
                .overlay(RoundedRectangle(cornerRadius: 12)
                    .stroke(didCopy ? Palette.yellow.opacity(0.6) : Palette.border, lineWidth: 1))
        }
    }

    private var rendered: String {
        let values = session.codes.map(\.value)
        switch format {
        case .numbered:
            return values.enumerated().map { idx, v in String(format: "%03d. %@", idx + 1, v) }.joined(separator: "\n")
        case .raw:
            return values.joined(separator: "\n")
        case .spaced:
            return values.joined(separator: " ")
        case .commad:
            return values.joined(separator: ",")
        }
    }

    /// Short, sortable, descriptive: `codes-20260503-1127-12.txt`.
    private var filename: String {
        let f = DateFormatter()
        f.dateFormat = "yyyyMMdd-HHmm"
        return "codes-\(f.string(from: exportDate))-\(session.codes.count).txt"
    }

    /// Human-readable date for headers and share subject.
    private var humanDate: String {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        return f.string(from: exportDate)
    }

    /// Used by Mail's subject line, by Notes as the title hint, and by
    /// other share targets that want a one-line summary.
    private var shareSubject: String {
        "BulkPokeScan · \(session.codes.count) codes · \(humanDate)"
    }

    /// File contents include a one-line header so when iOS Notes saves a
    /// `.txt` and uses the FIRST LINE OF TEXT as the note title, the title
    /// is the header (e.g., "BulkPokeScan · 12 codes · May 3, 2026 at 11:27 PM")
    /// rather than the user's first scanned code value. Copy button uses
    /// `rendered` (header-less) so paste-into-form workflows aren't disrupted.
    private var renderedForFile: String {
        "\(shareSubject)\n\n" + rendered
    }

    /// Writes the export to a temp file and returns its URL. Sharing a file
    /// URL gives Files a proper filename and gives Notes a properly-named
    /// attachment. Notes won't embed the text inline (it always attaches
    /// when a file is offered) — that's the cost of getting Files right.
    private var fileURL: URL? {
        guard !session.codes.isEmpty else { return nil }
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(filename)
        do {
            try renderedForFile.write(to: url, atomically: true, encoding: .utf8)
            return url
        } catch {
            return nil
        }
    }
}

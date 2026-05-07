import SwiftUI
import UIKit

enum Typography {
    static func display(_ size: CGFloat, weight: Font.Weight = .bold) -> Font {
        if let name = registered("SpaceGrotesk", weight: weight) {
            return .custom(name, size: size)
        }
        return .system(size: size, weight: weight, design: .default)
    }

    static func body(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        if let name = registered("InterTight", weight: weight) {
            return .custom(name, size: size)
        }
        return .system(size: size, weight: weight, design: .default)
    }

    static func mono(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        if let name = registered("JetBrainsMono", weight: weight) {
            return .custom(name, size: size)
        }
        return .system(size: size, weight: weight, design: .monospaced)
    }

    private static func registered(_ family: String, weight: Font.Weight) -> String? {
        let suffix: String
        switch weight {
        case .bold, .heavy, .black: suffix = "-Bold"
        case .semibold:             suffix = "-SemiBold"
        case .medium:               suffix = "-Medium"
        default:                    suffix = "-Regular"
        }
        let name = family + suffix
        return UIFont(name: name, size: 12) != nil ? name : nil
    }
}

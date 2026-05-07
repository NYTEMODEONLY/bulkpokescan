import SwiftUI

enum Palette {
    static let red          = Color(hex: 0xE63946)
    static let redDeep      = Color(hex: 0xB0202E)
    static let redSoft      = Color(hex: 0xFF6B6B)
    static let yellow       = Color(hex: 0xFFCB05)
    static let yellowDeep   = Color(hex: 0xE5A100)
    static let yellowSoft   = Color(hex: 0xFFE066)
    static let gold         = Color(hex: 0xC9A227)

    static let bg           = Color(hex: 0x0B0D14)
    static let bg2          = Color(hex: 0x11131C)
    static let surface      = Color(hex: 0x161823)
    static let surface2     = Color(hex: 0x1C1F2D)
    static let surface3     = Color(hex: 0x232739)
    static let input        = Color(hex: 0x181B27)
    static let border       = Color(hex: 0x262A3B)
    static let borderStrong = Color(hex: 0x363B52)

    static let text         = Color(hex: 0xF1F2F7)
    static let text2        = Color(hex: 0xA4A7B6)
    static let textMuted    = Color(hex: 0x6E7287)
    static let textDisabled = Color(hex: 0x454962)

    static let success      = Color(hex: 0x34C759)
    static let warning      = Color(hex: 0xFF9F0A)
    static let danger       = Color(hex: 0xFF453A)
    static let scan         = Color(hex: 0x5AC8FA)
}

extension Color {
    init(hex: UInt32, alpha: Double = 1.0) {
        let r = Double((hex >> 16) & 0xFF) / 255.0
        let g = Double((hex >> 8) & 0xFF) / 255.0
        let b = Double(hex & 0xFF) / 255.0
        self.init(.sRGB, red: r, green: g, blue: b, opacity: alpha)
    }
}

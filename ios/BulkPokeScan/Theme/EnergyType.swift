import SwiftUI

enum EnergyType: CaseIterable {
    case fire, water, grass, electric, psychic, fighting, dark, fairy

    var color: Color {
        switch self {
        case .fire:     return Color(hex: 0xF45A2A)
        case .water:    return Color(hex: 0x3798E1)
        case .grass:    return Color(hex: 0x5FA84A)
        case .electric: return Color(hex: 0xFFCB05)
        case .psychic:  return Color(hex: 0xB563D6)
        case .fighting: return Color(hex: 0xC8623A)
        case .dark:     return Color(hex: 0x4D4D58)
        case .fairy:    return Color(hex: 0xE89AC0)
        }
    }

    /// Deterministic energy-type for a code string. Mirrors desktop's
    /// `widgets.py` per-code pip color so the same code renders the same
    /// pip on every device.
    static func forCode(_ value: String) -> EnergyType {
        var hash: UInt64 = 5381
        for byte in value.utf8 {
            hash = (hash &* 33) &+ UInt64(byte)
        }
        let all = EnergyType.allCases
        return all[Int(hash % UInt64(all.count))]
    }
}

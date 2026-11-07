import SwiftUI
import UIKit
import CoreText

/// South Dakota palette, from the land (provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only, with no team or school
/// marks (fans split between SDSU and USD; state-prompts/SOUTH_DAKOTA_PROMPT.md): Black Hills pine #1E4D3B (9.6:1 on white) for titles,
/// tint, the honors and oldest cards; Badlands clay #A4472E (white on it 6.0:1) for the hand-checked guide cards and chips; sun gold
/// #F2B51C only as a pin, title-shadow and fill under ink (#1A1A1A on it 9.5:1; as text on white it's 1.8:1); cream #F6F0E4 pages.
/// North Dakota Eats is blue and red, so the two read apart. The names `green`/`gold` are kept from Wisconsin Eats so the shared views
/// read the same; here `green` is pine and `gold` is clay.
enum Theme {
    static let green = Color(hex: 0x1E4D3B)      // Black Hills pine: titles, tint, primary text accents
    static let green2 = Color(hex: 0x2B6650)
    static let gold = Color(hex: 0xA4472E)       // Badlands clay: card fills under white text, chips
    static let goldSoft = Color(hex: 0xF4DED6)   // soft clay
    static let lime = Color(hex: 0xF2B51C)       // sun gold, fills only (hand-checked pins, the title shadow), under ink or pine
    static let limeSoft = Color(hex: 0xFCECC0)
    static let sand = Color(hex: 0xF6F0E4)       // the Home background, cream
    static let red = Color(hex: 0x1E4D3B)        // honors chips (pine); no MICHELIN pins here
    static let sandstone = Color(hex: 0x143628)  // a darker pine accent
    static let teal = Color(hex: 0x7A321F)       // a darker clay (9.1:1 on white)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xEFE8D8)
    static let surface3 = Color(hex: 0xE2D9C5)
    static let rule = Color(hex: 0xE2D9C5)
    static let rule2 = Color(hex: 0xC9BEA6)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// South Dakota Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: thin Badlands strata, the clay, gold and pale layers of a butte's wall, each edge dipping a little the way the
/// beds do along the Wall. One element, no buttes (North Dakota's header has its prairie horizon).
struct Stripes: View {
    var height: CGFloat = 6

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height
            let bands = [Theme.gold, Theme.lime, Theme.goldSoft, Theme.gold, Theme.teal]
            let steps = 48
            // the y of the edge above band k at step i: flat at the top and bottom, waving between
            func edge(_ k: Int, _ i: Int) -> CGFloat {
                let y = h * CGFloat(k) / CGFloat(bands.count)
                guard k > 0 && k < bands.count else { return y }
                return y + CGFloat(sin(Double(i) / Double(steps) * .pi * 5 + Double(k) * 1.3)) * h * 0.06
            }
            for (k, color) in bands.enumerated() {
                var p = Path()
                for i in 0...steps {
                    let pt = CGPoint(x: w * CGFloat(i) / CGFloat(steps), y: edge(k, i))
                    if i == 0 { p.move(to: pt) } else { p.addLine(to: pt) }
                }
                for i in stride(from: steps, through: 0, by: -1) {
                    p.addLine(to: CGPoint(x: w * CGFloat(i) / CGFloat(steps), y: edge(k + 1, i)))
                }
                p.closeSubpath()
                ctx.fill(p, with: .color(color))
            }
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}

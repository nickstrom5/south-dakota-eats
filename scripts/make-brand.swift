// South Dakota Eats brand (provisional, 2026-11-06; Nick picks the name, icon and palette): the app icon is concept A of
// scripts/icon-concepts.swift, chislic (four seared cubes, a toothpick standing in each top one) on Black Hills pine; the shared Eats Ranked
// icon style, state-prompts/ICON-STYLE.md, no backing shape. No Mount Rushmore faces, no team or school marks.
// Usage, from sd-eats/: swift scripts/make-brand.swift   -> SouthDakotaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG (LOGO): change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let PINE: UInt32 = 0x1E4D3B, MEAT: UInt32 = 0x8A4B2A, CRUST: UInt32 = 0x6A3519, PICK: UInt32 = 0xF0D9A8
let CLAY: UInt32 = 0xA4472E, CLAYSOFT: UInt32 = 0xF4DED6, CLAYDARK: UInt32 = 0x7A321F, SUN: UInt32 = 0xF2B51C

func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}

/// A: chislic. CoreGraphics y-up, s = canvas size. Identical to icon-concepts.swift's concept A.
func chislic(_ c: CGContext, _ s: CGFloat) {
    let cube: CGFloat = 0.27, gap: CGFloat = 0.03, x0: CGFloat = 0.215, y0: CGFloat = 0.19
    c.setFillColor(rgb(PICK))
    for col in 0..<2 {
        let cx = x0 + CGFloat(col) * (cube + gap) + cube / 2
        c.addPath(R(s, cx - 0.016, y0 + cube + gap + cube - 0.05, 0.032, 0.17, 0.016)); c.fillPath()
    }
    for row in 0..<2 {
        for col in 0..<2 {
            let x = x0 + CGFloat(col) * (cube + gap), y = y0 + CGFloat(row) * (cube + gap)
            c.setFillColor(rgb(CRUST)); c.addPath(R(s, x, y, cube, cube, 0.06)); c.fillPath()
            c.setFillColor(rgb(MEAT)); c.addPath(R(s, x, y + 0.05, cube, cube - 0.05, 0.06)); c.fillPath()
        }
    }
}

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(PINE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    chislic(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "SouthDakotaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): Black Hills pine, the chislic at the left, the name and tagline at the right, and the app's header band
/// along the bottom: thin Badlands strata in clay, sun gold and pale clay (Theme.swift's Stripes).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(PINE)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    // five strata, each top edge dipping a little, as in the app's header
    let bands = [CLAYDARK, CLAY, CLAYSOFT, SUN, CLAY], bandH: CGFloat = 13, steps = 60
    for (k, color) in bands.enumerated() {
        func edge(_ j: Int, _ i: Int) -> CGFloat {
            let y = bandH * CGFloat(j)
            guard j > 0 && j < bands.count else { return y }
            return y + CGFloat(sin(Double(i) / Double(steps) * .pi * 9 + Double(j) * 1.3)) * 3
        }
        let p = CGMutablePath()
        for i in 0...steps { let pt = CGPoint(x: CGFloat(W) * CGFloat(i) / CGFloat(steps), y: edge(k, i)); if i == 0 { p.move(to: pt) } else { p.addLine(to: pt) } }
        for i in stride(from: steps, through: 0, by: -1) { p.addLine(to: CGPoint(x: CGFloat(W) * CGFloat(i) / CGFloat(steps), y: edge(k + 1, i))) }
        p.closeSubpath(); ctx.setFillColor(rgb(color)); ctx.addPath(p); ctx.fillPath()
    }
    ctx.saveGState(); ctx.translateBy(x: 40, y: 90); chislic(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 80) ?? NSFont.boldSystemFont(ofSize: 70)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 34) ?? NSFont.boldSystemFont(ofSize: 30)
    NSAttributedString(string: "SOUTH DAKOTA", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 380))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 296))
    NSAttributedString(string: "CHISLIC, BISON & WALLEYE", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.949, green: 0.710, blue: 0.110, alpha: 1)]).draw(at: NSPoint(x: 564, y: 246))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")

// South Dakota Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level, centred
// food on Black Hills pine #1E4D3B (the prompt's second palette; North Dakota is blue), no backing shape, no text or texture, no Mount
// Rushmore faces, no team or school marks.
// Food hexes: seared meat #8A4B2A, its crust #6A3519, toothpicks #F0D9A8; kuchen dough #D9A04A, custard #F6E3A1, plums #7A2E4A;
// frybread #D9A04A, beef #6E3B1F, lettuce #9CC46B, tomato #D9452B, cheese #F2B705.
//   A  chislic: four seared cubes of lamb or beef, a toothpick in each, side elevation
//   B  a slice of kuchen, side elevation: sweet dough under custard, plums on top
//   C  an Indian taco: frybread with beef, lettuce, tomato and cheese, side elevation
// Usage, from sd-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let PINE: UInt32 = 0x1E4D3B, MEAT: UInt32 = 0x8A4B2A, CRUST: UInt32 = 0x6A3519, PICK: UInt32 = 0xF0D9A8
let DOUGH: UInt32 = 0xD9A04A, CUSTARD: UInt32 = 0xF6E3A1, PLUM: UInt32 = 0x7A2E4A
let BEEF: UInt32 = 0x6E3B1F, LETTUCE: UInt32 = 0x9CC46B, TOMATO: UInt32 = 0xD9452B, CHEESE: UInt32 = 0xF2B705

func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}

/// A: chislic, four seared cubes in two rows, a toothpick standing in each top cube and leaning out of each bottom one's side gap.
/// CoreGraphics y-up. Identical to make-brand.swift's chislic() and make-site.py's LOGO.
func chislic(_ c: CGContext, _ s: CGFloat) {
    let cube: CGFloat = 0.27, gap: CGFloat = 0.03, x0: CGFloat = 0.215, y0: CGFloat = 0.19
    // toothpicks first, so the cubes sit over their feet: one up out of each top cube
    c.setFillColor(rgb(PICK))
    for col in 0..<2 {
        let cx = x0 + CGFloat(col) * (cube + gap) + cube / 2
        c.addPath(R(s, cx - 0.016, y0 + cube + gap + cube - 0.05, 0.032, 0.17, 0.016)); c.fillPath()
    }
    for row in 0..<2 {
        for col in 0..<2 {
            let x = x0 + CGFloat(col) * (cube + gap), y = y0 + CGFloat(row) * (cube + gap)
            c.setFillColor(rgb(CRUST)); c.addPath(R(s, x, y, cube, cube, 0.06)); c.fillPath()            // the seared crust
            c.setFillColor(rgb(MEAT)); c.addPath(R(s, x, y + 0.05, cube, cube - 0.05, 0.06)); c.fillPath()   // the cube's face above it
        }
    }
}

/// B: a slice of kuchen in side elevation: a dough base, a thick custard layer, three plum halves on top.
func kuchen(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(DOUGH)); c.addPath(R(s, 0.14, 0.30, 0.72, 0.12, 0.05)); c.fillPath()
    c.setFillColor(rgb(CUSTARD)); c.addPath(R(s, 0.14, 0.40, 0.72, 0.18, 0.05)); c.fillPath()
    c.setFillColor(rgb(PLUM))
    for x in [0.20, 0.405, 0.61] as [CGFloat] {
        c.addPath(R(s, x, 0.55, 0.19, 0.13, 0.065)); c.fillPath()
    }
}

/// C: an Indian taco in side elevation: the frybread round, then beef, lettuce, tomato and cheese.
func taco(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(DOUGH)); c.addPath(R(s, 0.14, 0.30, 0.72, 0.16, 0.08)); c.fillPath()        // frybread
    c.setFillColor(rgb(BEEF)); c.addPath(R(s, 0.18, 0.44, 0.64, 0.09, 0.045)); c.fillPath()        // seasoned beef
    c.setFillColor(rgb(LETTUCE)); c.addPath(R(s, 0.21, 0.51, 0.58, 0.08, 0.04)); c.fillPath()      // shredded lettuce
    c.setFillColor(rgb(TOMATO))
    for x in [0.25, 0.43, 0.61] as [CGFloat] { c.addPath(R(s, x, 0.58, 0.14, 0.07, 0.035)); c.fillPath() }   // diced tomato
    c.setFillColor(rgb(CHEESE)); c.addPath(R(s, 0.30, 0.64, 0.40, 0.07, 0.035)); c.fillPath()      // cheese on top
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(PINE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", chislic)
render(1024, out + "/concept-b-1024.png", kuchen)
render(1024, out + "/concept-c-1024.png", taco)

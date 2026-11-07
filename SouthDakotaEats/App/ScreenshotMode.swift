import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, chislic, bison, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // downtown Sioux Falls (Phillips Avenue), so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 43.5470, longitude: -96.7290)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("The Pheasant Restaurant & Lounge", "Brookings"), pick("Dakotah Steakhouse", "Rapid City"), pick("The Barrel House", "Sioux Falls")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "chislic": open(.chislic)
        case "bison":
            // downtown Rapid City
            model.screenshotLocation = CLLocation(latitude: 44.0805, longitude: -103.2310)
            open(.bison)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // The Pheasant in Brookings: chislic, its 1949 founding year and the James Beard Foundation's 2024 America's Classic
            model.screenshotLocation = CLLocation(latitude: 44.3114, longitude: -96.7984)
            open(.chislic)
            if let p = pick("The Pheasant Restaurant & Lounge", "Brookings") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("The Pheasant Restaurant & Lounge", "Brookings")
        case "chislic": pick("The Barrel House", "Sioux Falls")
        case "bison": pick("Dakotah Steakhouse", "Rapid City")
        case "map": pick("Ode to Food and Drinks", "Sioux Falls")
        case "honors": pick("BibiSol", "Sioux Falls")
        case "oldest": pick("The Pheasant Restaurant & Lounge", "Brookings")
        case "saved": pick("Dakotah Steakhouse", "Rapid City")
        case "about": nil
        default: pick("The Pheasant Restaurant & Lounge", "Brookings")
        }
        model.selectedPlace = place
    }
}

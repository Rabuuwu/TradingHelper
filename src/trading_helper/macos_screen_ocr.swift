import AppKit
import Foundation
import Vision

struct BrowserWindow: Codable {
    let id: UInt32
    let app: String
    let title: String
}

struct TextObservation: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct OCRResult: Codable {
    let window: BrowserWindow
    let observations: [TextObservation]
}

struct Failure: Codable {
    let error: String
}

func output<T: Encodable>(_ value: T) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys]
    if let data = try? encoder.encode(value), let text = String(data: data, encoding: .utf8) {
        print(text)
    } else {
        print("{\"error\":\"json encoding failed\"}")
    }
}

func browserWindows() -> [BrowserWindow] {
    let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
    let rows = (CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]]) ?? []
    let browsers = [
        "safari", "chrome", "chromium", "firefox", "arc", "edge", "brave", "opera",
        "vivaldi", "orion", "duckduckgo",
    ]
    let candidates = rows.compactMap { row -> BrowserWindow? in
        let title = row[kCGWindowName as String] as? String ?? ""
        guard
            let id = row[kCGWindowNumber as String] as? UInt32,
            let app = row[kCGWindowOwnerName as String] as? String,
            let bounds = row[kCGWindowBounds as String] as? [String: Any],
            let width = bounds["Width"] as? Double,
            let height = bounds["Height"] as? Double,
            width > 300,
            height > 200,
            browsers.contains(where: { app.lowercased().contains($0) })
        else { return nil }
        return BrowserWindow(id: id, app: app, title: title)
    }
    let matches = candidates.filter { $0.title.localizedCaseInsensitiveContains("TradingView") }
    fputs(
        "OCR_DIAG visible_windows=\(rows.count) browser_windows=\(candidates.count) " +
            "tradingview_title_matches=\(matches.count)\n",
        stderr
    )
    for window in candidates {
        let titleMatches = window.title.localizedCaseInsensitiveContains("TradingView")
        fputs(
            "OCR_DIAG browser=\(window.app) title_chars=\(window.title.count) " +
                "tradingview_title=\(titleMatches)\n",
            stderr
        )
    }
    // Some browser builds (including Firefox on some macOS releases) expose an
    // empty CGWindowName. Return all visible browser windows so the caller can
    // verify those titleless windows from local OCR instead of dropping them.
    return candidates
}

func run(_ arguments: [String]) -> Never {
    guard arguments.count >= 2 else {
        output(Failure(error: "usage: screen-ocr browser-windows | screen-ocr read WINDOW_ID"))
        exit(2)
    }
    if arguments[1] == "browser-windows" {
        output(browserWindows())
        exit(0)
    }
    guard arguments[1] == "read", arguments.count == 3, let wantedID = UInt32(arguments[2]) else {
        output(Failure(error: "usage: screen-ocr browser-windows | screen-ocr read WINDOW_ID"))
        exit(2)
    }
    guard let window = browserWindows().first(where: { $0.id == wantedID }) else {
        output(Failure(error: "selected TradingView browser window is no longer visible"))
        exit(3)
    }
    guard let image = CGWindowListCreateImage(
        .null,
        .optionIncludingWindow,
        wantedID,
        [.bestResolution, .boundsIgnoreFraming]
    ) else {
        output(Failure(error: "screen capture unavailable; grant Screen Recording permission"))
        exit(4)
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    do {
        let supportedLanguages = try request.supportedRecognitionLanguages()
        request.recognitionLanguages = ["en-US", "pl-PL"].filter {
            supportedLanguages.contains($0)
        }
        try VNImageRequestHandler(cgImage: image).perform([request])
        let observations = (request.results ?? []).compactMap { item -> TextObservation? in
            guard let candidate = item.topCandidates(1).first, !candidate.string.isEmpty else {
                return nil
            }
            let box = item.boundingBox
            return TextObservation(
                text: candidate.string,
                confidence: candidate.confidence,
                x: box.origin.x,
                y: box.origin.y,
                width: box.width,
                height: box.height
            )
        }
        output(OCRResult(window: window, observations: observations))
        exit(0)
    } catch {
        output(Failure(error: "Vision OCR failed"))
        exit(5)
    }
}

run(CommandLine.arguments)

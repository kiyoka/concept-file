import Foundation

struct Temperature {
    var celsius: Double
    var fahrenheit: Double {
        return celsius * 9 / 5 + 32
    }
}

enum WeatherCondition {
    case sunny
    case cloudy
    case rainy
    case snowy
}

protocol WeatherProvider {
    func currentWeather(for city: String) -> Weather
    func forecast(for city: String, days: Int) -> [Weather]
}

class Weather {
    var city: String
    var temperature: Temperature
    var condition: WeatherCondition

    init(city: String, temperature: Temperature, condition: WeatherCondition) {
        self.city = city
        self.temperature = temperature
        self.condition = condition
    }

    func description() -> String {
        return "\(city): \(temperature.celsius)°C, \(condition)"
    }
}

class WeatherService: WeatherProvider {
    var apiKey: String
    var cache: [String: Weather]

    init(apiKey: String) {
        self.apiKey = apiKey
        self.cache = [:]
    }

    func currentWeather(for city: String) -> Weather {
        if let cached = cache[city] {
            return cached
        }
        let weather = Weather(
            city: city,
            temperature: Temperature(celsius: 20.0),
            condition: .sunny
        )
        cache[city] = weather
        return weather
    }

    func forecast(for city: String, days: Int) -> [Weather] {
        return (0..<days).map { _ in
            Weather(city: city, temperature: Temperature(celsius: 18.0), condition: .cloudy)
        }
    }

    func clearCache() {
        cache.removeAll()
    }
}

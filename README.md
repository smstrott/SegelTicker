# SegelTicker

SegelTicker verwandelt stündliche Wetterprognosen in konkrete Empfehlungen für
Seglerinnen und Segler. Für jeden Standort bewertet der Dienst überlappende
3-Stunden-Fenster, ermittelt den besten Zeitraum und erzeugt eine kompakte
Telegram-Nachricht sowie zwei Dashboard-Grafiken für heute und morgen.

## Funktionen

- Bewertung stabiler Segelfenster von mindestens drei Stunden
- Wind, Böen, Windrichtung, Temperatur und Niederschlag
- bestes und weitere geeignete Segelfenster
- kompakter Ausblick für die folgenden Tage
- mehrere Telegram-Topics und Standorte
- sicherer Dry-Run und lokale Beispieldaten
- Timeouts, Retries und isolierte Fehlerbehandlung je Standort

## Voraussetzungen

- Python 3.9 oder neuer
- OpenWeather One Call API 3.0
- Telegram-Bot und eine Chat-/Gruppen-ID
- bei Telegram-Topics zusätzlich die jeweilige Topic-ID

## Installation

```bash
git clone <REPOSITORY-URL>
cd SegelTicker

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Konfiguration

Die lokale Konfiguration wird nicht versioniert:

```bash
cp config.example.json config.json
```

Danach in `config.json` eintragen:

- `telegram.token`: Token des Telegram-Bots
- `telegram.chat_id`: Zielgruppe oder Zielchat
- `openweathermap.app_id`: OpenWeather API-Key
- `locations`: Name, Topic-ID, Breitengrad und Längengrad je Revier

Beim Start werden alle Pflichtfelder, Koordinaten und doppelte Standortnamen
validiert. Zugangsdaten gehören niemals in Python-Dateien oder Commits.

Falls ein Token bereits veröffentlicht oder in Git committed wurde, muss er beim
jeweiligen Anbieter widerrufen und neu erzeugt werden. Das Entfernen aus der
aktuellen Datei löscht ihn nicht aus der Git-Historie.

## Sicher testen

Lokale Beispieldaten verwenden; dabei erfolgen weder Wetter- noch
Telegram-Netzwerkaufrufe:

```bash
python wind_plot.py \
  --sample-data example_wind_data.json \
  --location Wannsee
```

Aktuelle Wetterdaten abrufen, aber nichts an Telegram senden:

```bash
python wind_plot.py --dry-run --location Wannsee
```

Alle konfigurierten Standorte mit Live-Daten lokal prüfen:

```bash
python wind_plot.py --dry-run
```

Die Vorschau schreibt die Dashboard-Bilder in das aktuelle Arbeitsverzeichnis
und gibt die Telegram-Nachricht im Terminal aus.

## Tests

```bash
python -m unittest discover -v
```

Die Tests verwenden simulierte Netzwerkantworten und versenden keine echten
Telegram-Nachrichten.

## Produktiver Start

Ohne Argumente werden alle konfigurierten Standorte verarbeitet und versendet:

```bash
python wind_plot.py
```

Vor dem ersten produktiven Lauf immer zunächst `--sample-data` und anschließend
`--dry-run` ausführen.

## Cron-Beispiel

Der folgende Eintrag startet SegelTicker täglich um 08:00 Uhr. Pfade müssen an
den Server angepasst werden:

```cron
0 8 * * * cd /opt/segelticker && /opt/segelticker/.venv/bin/python wind_plot.py >> /var/log/segelticker.log 2>&1
```

Die Server-Zeitzone sollte auf `Europe/Berlin` eingestellt sein. SegelTicker
selbst rechnet Wetterzeitstempel explizit nach Berlin um.

## Projektstruktur

```text
wind_plot.py          Programmstart und Standort-Orchestrierung
weather_client.py     OpenWeather-API, Timeouts und Retries
telegram_client.py    Telegram-Nachrichten und Fotos
weather_analysis.py   Wetteraufbereitung und Segelfenster
sailing_score.py      Bewertungsprofil und Score
sailing_windows.py    Suche und Verbindung geeigneter Zeiträume
message_formatter.py  Telegram-Text
dashboard_plot.py     Dashboard-Grafiken
config_loader.py      Konfigurationsvalidierung
```

## Fehlerverhalten

Ein Fehler an einem Standort stoppt die übrigen Standorte nicht. Nach dem Lauf
endet das Programm dennoch mit einem Fehlerstatus und nennt alle fehlgeschlagenen
Standorte, damit Cron oder Monitoring den unvollständigen Lauf erkennen kann.

Wetter-GETs werden bei temporären HTTP-Fehlern wiederholt. Telegram-POSTs werden
nicht automatisch wiederholt, um doppelte Nachrichten zu vermeiden.

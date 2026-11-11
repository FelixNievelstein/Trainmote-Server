# Trainmote Server (Node.js / TypeScript)

Node.js-Server für einen Raspberry Pi, der eine Modelleisenbahn über die GPIOs steuern soll.
Er stellt eine REST-API und einen WebSocket bereit und speichert Daten in SQLite (über Prisma).

> **⚠️ Aktueller Stand: Prototyp, steuert noch keine Hardware**
>
> - Die GPIO-Schicht ([src/lib/gpio.ts](src/lib/gpio.ts)) ist **ausschließlich ein Mock**. Auch auf dem Raspberry Pi wird kein Pin geschaltet.
> - Die API ist **nicht kompatibel** mit dem Python-Original (`/trainmote/api/v1/...`, Port 5000, Basic Auth). Bestehende Trainmote-Clients funktionieren mit diesem Server nicht.
> - Weichen, Haltepunkte, Programme/Aktionen, Konfiguration, Benutzer und Geräte-Endpunkte aus der Python-Version fehlen noch.
> - Die API hat **keine Authentifizierung**. Jeder im Netzwerk kann sie aufrufen.
>
> Details siehe [Bekannte Probleme](#bekannte-probleme).

---

## Voraussetzungen

| Komponente | Version |
|---|---|
| Node.js | 20 LTS oder 22 LTS (mindestens 18) |
| npm | wird mit Node.js installiert |
| Betriebssystem | Raspberry Pi OS (64-bit empfohlen) oder macOS/Linux für die Entwicklung |

Node.js auf dem Raspberry Pi installieren (Beispiel für Node 22 über NodeSource):

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v
```

## Installation

```bash
git clone https://github.com/FelixNievelstein/Trainmote-Server.git
cd Trainmote-Server/npm
npm install
```

### Konfiguration (`.env`)

Die Datei `.env` ist in `.gitignore` eingetragen und muss nach dem Klonen angelegt werden:

```bash
cat > .env <<'EOF'
PORT=3000
DATABASE_URL="file:./trainmote.db"
EOF
```

| Variable | Standard | Bedeutung |
|---|---|---|
| `PORT` | `3000` | HTTP- und WebSocket-Port |
| `DATABASE_URL` | `file:./trainmote.db` | SQLite-Datei. Der Pfad ist **relativ zu `prisma/schema.prisma`**, die Datenbank liegt also unter `prisma/trainmote.db`. |

### Datenbank anlegen

```bash
npm run prisma:push
```

Das legt die SQLite-Datenbank mit den Tabellen aus [prisma/schema.prisma](prisma/schema.prisma) an und erzeugt den Prisma-Client.
Nach jeder Änderung am Schema muss der Befehl erneut ausgeführt werden.

## Server starten

### Entwicklung (mit automatischem Neustart)

```bash
npm run dev
```

Ausgabe:

```
Trainmote server listening on http://localhost:3000
```

### Produktion

```bash
npm run build   # TypeScript nach dist/ kompilieren
npm start       # node dist/server.js
```

> **Hinweis:** `npm run build` schlägt derzeit mit Typfehlern in [src/lib/trainMachine.ts](src/lib/trainMachine.ts) fehl (siehe [Bekannte Probleme](#bekannte-probleme)). Bis das behoben ist, funktioniert nur `npm run dev`.

### Autostart auf dem Raspberry Pi (systemd)

`/etc/systemd/system/trainmote.service` anlegen (Benutzer und Pfad anpassen):

```ini
[Unit]
Description=Trainmote Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Trainmote-Server/npm
ExecStart=/usr/bin/node dist/server.js
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now trainmote
journalctl -u trainmote -f     # Logs ansehen
```

> Der Server reagiert derzeit nur auf `SIGINT`, nicht auf `SIGTERM`. `systemctl stop` beendet ihn also ohne GPIO-Aufräumen. Sobald echte GPIOs angesteuert werden, muss das behoben sein.

## Verwendung

Alle Beispiele gehen von `http://localhost:3000` aus. Auf einem anderen Gerät im Netzwerk stattdessen die IP des Raspberry Pi verwenden (`hostname -I`).

### REST-API

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Lebenszeichen und aktueller Zustand der Zustandsmaschine |
| `GET` | `/api/trains` | Alle Züge auflisten |
| `POST` | `/api/trains` | Zug anlegen |
| `POST` | `/api/trains/:id/command` | Befehl an einen Zug senden |

#### Statusabfrage

```bash
curl http://localhost:3000/health
# {"ok":true,"state":"idle"}
```

#### Zug anlegen

```bash
curl -X POST http://localhost:3000/api/trains \
  -H 'Content-Type: application/json' \
  -d '{"name": "ICE", "address": 3}'
```

| Feld | Typ | Pflicht |
|---|---|---|
| `name` | string | ja |
| `address` | number | ja |

Antwort `201` mit dem angelegten Zug. Fehlt ein Feld, kommt `400`.

#### Züge auflisten

```bash
curl http://localhost:3000/api/trains
```

#### Befehl an einen Zug senden

```bash
# Starten
curl -X POST http://localhost:3000/api/trains/1/command \
  -H 'Content-Type: application/json' \
  -d '{"action": "start"}'

# Geschwindigkeit und Richtung setzen
curl -X POST http://localhost:3000/api/trains/1/command \
  -H 'Content-Type: application/json' \
  -d '{"speed": 50, "direction": "forward"}'

# Stoppen
curl -X POST http://localhost:3000/api/trains/1/command \
  -H 'Content-Type: application/json' \
  -d '{"action": "stop"}'
```

| Feld | Werte | Wirkung |
|---|---|---|
| `action` | `"start"` / `"stop"` | Schaltet GPIO 17 (BCM) auf 1 bzw. 0 (zurzeit nur im Mock) |
| `speed` | Zahl, 0–100 | Geschwindigkeit |
| `direction` | `"forward"`, `"backward"`, `"stop"` | Fahrtrichtung |

Antwort:

```json
{
  "ok": true,
  "train": { "id": 1, "name": "ICE", "address": 3, "speed": 50, "direction": "forward", "isActive": true },
  "machine": { "speed": 50, "direction": "forward" }
}
```

`train` ist der gespeicherte Datensatz, `machine` der Zustand der Zustandsmaschine. Die beiden können voneinander abweichen (siehe [Bekannte Probleme](#bekannte-probleme)).

### WebSocket

Endpunkt: `ws://localhost:3000/ws`

Direkt nach dem Verbinden sendet der Server den aktuellen Status:

```json
{"type": "status", "payload": {"state": "idle"}}
```

Jede Nachricht des Clients wird mit dem aktuellen Status beantwortet. Eine Nachricht mit `"type": "command"` setzt die Zustandsmaschine auf `running`:

```json
{"type": "command"}
```

Ungültiges JSON führt zu:

```json
{"type": "error", "payload": {"message": "..."}}
```

Schnell testen (ohne Installation):

```bash
npx wscat -c ws://localhost:3000/ws
```

Änderungen über die REST-API werden **nicht** an verbundene WebSocket-Clients gesendet.

## Projektstruktur

```
npm/
├── prisma/schema.prisma     Datenbankschema (Train, Route)
├── src/
│   ├── server.ts            Express-Server, REST-Routen, WebSocket
│   ├── config.ts            Liest PORT und DATABASE_URL aus .env
│   ├── types.ts             DTO-Typen (derzeit ungenutzt)
│   └── lib/
│       ├── gpio.ts          GPIO-Schnittstelle + Mock-Implementierung
│       ├── prisma.ts        Prisma-Client
│       └── trainMachine.ts  XState-Zustandsmaschine (idle / running)
├── package.json
└── tsconfig.json
```

## npm-Skripte

| Skript | Beschreibung |
|---|---|
| `npm run dev` | Startet den Server mit `tsx` und Neustart bei Dateiänderungen |
| `npm run build` | Kompiliert TypeScript nach `dist/` |
| `npm start` | Startet die kompilierte Version aus `dist/` |
| `npm run prisma:generate` | Erzeugt den Prisma-Client neu |
| `npm run prisma:push` | Gleicht die Datenbank mit dem Schema ab (ohne Migrationen) |
| `npm run prisma:migrate` | Erstellt eine Migration namens `init` (nur für die erste Migration geeignet) |

## Bekannte Probleme

**Stabilität**
- Eine einzige ungültige Anfrage beendet den gesamten Server. Beispiel: `POST /api/trains` mit `{"name": {"x":1}, "address": 1}`. Die async-Handler fangen Datenbankfehler nicht ab, und Express 4 leitet abgelehnte Promises nicht weiter.
- `npm run build` scheitert: In `trainMachine.ts` fehlen die Event-Typen für XState (`Property 'value' does not exist on type 'EventObject'`).

**Logik**
- Es gibt nur **eine** globale Zustandsmaschine für alle Züge. Startet man Zug 1, meldet auch Zug 2 den Zustand `running`.
- Eingaben werden ungeprüft gespeichert: `speed: 500` oder `direction: "sideways"` landen so in der Datenbank. Nur die Zustandsmaschine begrenzt auf 0–100.
- Nach `stop` bleibt `direction` in der Datenbank auf dem alten Wert, die Zustandsmaschine meldet dagegen `stop`.
- Ein Befehl ohne `action` (z. B. nur `speed`) setzt `isActive` auf `true`, auch wenn der Zug gestoppt ist.
- Alle Züge schalten denselben, fest einprogrammierten GPIO 17. Die `address` des Zugs wird nicht verwendet.

**Hardware und Betrieb**
- Es gibt keine echte GPIO-Implementierung, nur den Mock.
- Es gibt keine Authentifizierung, und CORS ist für alle Origins offen.
- `SIGTERM` wird nicht behandelt (relevant für systemd).

**Funktionsumfang gegenüber der Python-Version**
Noch nicht portiert: Weichen (`/switch`), Haltepunkte (`/stoppoint`), Konfiguration (Power-, Weichenstrom- und Status-Relais), Programme mit Aktionen (`SetSwitch`, `SetStop`, `WaitFor`, `StartAtClock`), Benutzer mit Basic Auth, Geräte-Endpunkte (Neustart, Herunterfahren, Update), Status-LED, Abschalt-Taster und Pin-Validierung. Bestehende Datenbanken der Python-Version (`/content/tom-db.sqlite`) werden nicht übernommen.

## Lizenz

MIT, siehe [LICENSE](../LICENSE).

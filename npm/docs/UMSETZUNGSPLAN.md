# Umsetzungsplan Trainmote Server (Node.js)

Dieser Plan beschreibt zwei Arbeitspakete:

- **Phase 1:** Den vorhandenen Node-Code stabilisieren (Build, Fehlerbehandlung, Validierung, Shutdown).
- **Phase 2:** Den Funktionsumfang des Python-Servers vollständig nach Node portieren, inklusive echter GPIO-Ansteuerung.

Jeder Schritt ist ein eigener Pull Request (PR), der für sich reviewbar, lauffähig und getestet ist.

---

## 0. Spielregeln

### 0.1 Größenlimit pro PR: max. 300 geänderte Zeilen

Gezählt wird `added + deleted` aus `git diff --numstat <base>...HEAD`, **inklusive Tests**.

Ausgenommen sind nur:

| Ausnahme | Grund |
|---|---|
| `package-lock.json` | generiert |
| `prisma/migrations/**/migration.sql` | von Prisma generiert, wird beim Review nur überflogen |
| PRs, die **ausschließlich löschen** | eine reine Löschung braucht kein Zeilen-Review |

Wird ein PR beim Umsetzen größer als geplant, wird er geteilt. Die Schätzungen unten lassen dafür Puffer. PR 1.1 führt ein Skript ein, das das Limit in CI prüft.

### 0.2 Definition of Done (für jeden PR)

- `npm run typecheck` und `npm test` laufen grün (lokal und in CI).
- Neue Logik hat Tests. Hardwareabhängiges wird gegen den Mock-Treiber getestet.
- Server startet mit `npm run dev` und mit `npm run build && npm start`.
- README ist angepasst, falls sich Bedienung oder API ändern.
- PRs mit Hardwarebezug: manuelle Prüfung auf dem Pi laut Checkliste im PR, Ergebnis im PR vermerkt.

### 0.3 Branching

- Basis-Branch: `develop`. Ein Branch pro PR: `node/<pr-nummer>-<kurzname>`, z. B. `node/1.3-error-handling`.
- PRs werden in der angegebenen Reihenfolge gemergt. Wo die Abhängigkeiten es erlauben, ist Parallelarbeit möglich (siehe Abhängigkeitsgraph).
- Der Python-Code bleibt bis PR 2.20 unverändert im Repo.

---

## 1. Entscheidungen vor dem Start

Diese Punkte bestimmen den Zuschnitt einiger PRs. Die Empfehlung ist jeweils fett.

| # | Frage | Optionen | Empfehlung |
|---|---|---|---|
| E1 | Bleibt das Train-Modell (`/api/trains`, Geschwindigkeit, Richtung, DCC-Adresse) erhalten? | behalten / entfernen | **Entfernen.** Die Hardware schaltet Relais (Weichen, Halteabschnitte). Für Geschwindigkeit, Richtung und DCC-Adressen gibt es dort keine Entsprechung. |
| E2 | Soll die neue API mit der bestehenden Trainmote-App kompatibel sein? | kompatibel / neu entwerfen | **Kompatibel:** gleiche Pfade (`/trainmote/api/v1/...`), Feldnamen, Statuscodes, Basic Auth, Standardport 5000. Offensichtliche Fehler werden behoben und in `docs/KOMPATIBILITAET.md` dokumentiert. |
| E3 | Wie werden bestehende Installationen übernommen? | neu einrichten / Import | **Import-Skript** für `/content/tom-db.sqlite`, einschließlich der Passwort-Hashes |
| E4 | Welche GPIO-Bibliothek? | `node-libgpiod`, `opengpio`, `onoff`, `pigpio` | **libgpiod-basiert** (`node-libgpiod`), endgültig nach Spike in PR 2.3. `onoff` (sysfs) und `pigpio` funktionieren auf dem Pi 5 bzw. aktuellen Kerneln nicht zuverlässig. |
| E5 | Zustandsmaschine für Programme | XState / eigene Klasse | **Eigene `ProgramRunner`-Klasse** mit `async`/`AbortController`. Sie ist kleiner, besser testbar, und die Abhängigkeit `xstate` entfällt. |
| E6 | Validierung | `ajv` mit den vorhandenen JSON-Schemas / `zod` | **`zod`**, weil die TypeScript-Typen direkt aus dem Schema entstehen. Die Python-Schemas werden 1:1 nachgebaut. |
| E7 | Node-Version | 18 / 20 / 22 | **22 LTS** (Entwicklung und Pi), `engines: ">=20"`. Node 18 ist End-of-Life. |

**Auswirkung von E1:** Wird das Train-Modell entfernt (Empfehlung), sind die PRs **1.5 und 1.7 überflüssig** und werden übersprungen. Die übrigen PRs aus Phase 1 schaffen die Grundlage (Build, Tests, Fehlerbehandlung, Validierung, Shutdown), auf der Phase 2 aufbaut.

---

## Phase 1: Vorhandenen Code stabilisieren

### PR 1.1: Build reparieren, Tooling, PR-Größen-Check (~90 Zeilen)

**Ziel:** `npm run build` läuft, CI prüft jeden PR.

- `src/lib/trainMachine.ts`: Machine typisieren mit `createMachine<TrainContext, TrainCommand>(...)` und `predictableActionArguments: true` setzen. Behebt die vier `TS2339`-Fehler und die Laufzeitwarnung.
- `package.json`:
  - Skript `typecheck` (`tsc --noEmit`)
  - Skript `postinstall` (`prisma generate`)
  - `engines.node: ">=20"`
  - `@types/express` auf `^4.17` (passend zu Express 4; in PR 1.3 folgt Express 5)
- `.env.example` anlegen. Die README verweist dann darauf statt auf das Heredoc.
- `scripts/check-diff-size.sh`: zählt die Zeilen laut 0.1 und bricht bei mehr als 300 ab.
- `.github/workflows/node.yml`: `npm ci`, `typecheck`, `build`, Größen-Check (nur bei PRs), Arbeitsverzeichnis `npm/`.

**Abnahme:** `npm run build && npm start` startet den Server. Der CI-Lauf ist grün.

### PR 1.2: Testinfrastruktur und `createApp()` (~220 Zeilen)

**Ziel:** HTTP-Endpunkte lassen sich ohne offenen Port und ohne echte DB-Datei testen.

- `src/app.ts`: `createApp(deps: { prisma, gpio, service })` gibt die Express-App zurück. `server.ts` macht nur noch den Bootstrap (Konfiguration, `listen`, WebSocket, Signale).
- Dev-Abhängigkeiten `vitest` und `supertest`, Skript `test`.
- `test/setup.ts`: eigene SQLite-Testdatenbank pro Testlauf (`DATABASE_URL=file:./test-<pid>.db`, `prisma db push --skip-generate` im `globalSetup`).
- Tests, die das **aktuelle** Verhalten festhalten: `/health`, Zug anlegen, Züge auflisten, `command` start/stop.
- CI: zusätzlich `npm test`.

**Abnahme:** `npm test` ist grün. Ein Diff vorher/nachher zeigt, dass sich das Verhalten nicht geändert hat.

### PR 1.3: Fehlerbehandlung, damit der Server nicht abstürzt (~150 Zeilen)

**Ziel:** Keine Anfrage kann den Prozess beenden.

- Upgrade auf **Express 5** (`express@^5`, `@types/express@^5`). Express 5 leitet abgelehnte Promises aus async-Handlern automatisch an die Fehler-Middleware weiter.
- `src/http/errors.ts`:
  - Klasse `HttpError(status, message)`
  - Fehler-Middleware mit Antwort immer `{"error": "<text>"}`
  - Abbildung: Prisma `P2025` → 404, `PrismaClientValidationError` → 400, `HttpError` → dessen Status, alles andere → 500 (Details nur im Log)
- 404-Handler für unbekannte Routen. Ungültiges JSON im Body ergibt 400 statt einer HTML-Fehlerseite.
- `process.on('unhandledRejection' | 'uncaughtException')`: Fehler loggen. Bei `uncaughtException` geordnet herunterfahren (Funktion aus PR 1.6, bis dahin `process.exit(1)`).
- Tests: der Absturzfall aus dem Review (`name` als Objekt), kaputtes JSON, unbekannte Route.

**Abnahme:** Der Reproduktionsfall liefert 400, und der Server läuft weiter.

### PR 1.4: Eingabevalidierung mit zod (~170 Zeilen)

- Abhängigkeit `zod`. `src/http/validate.ts` stellt `validateBody(schema)` als Middleware bereit; Fehler ergeben 400 mit Feldangabe.
- Schemas für den Prototyp:
  - `CreateTrain`: `name` 1–100 Zeichen, `address` als Ganzzahl 1–9999
  - `TrainCommand`: `action` ∈ {start, stop}, `speed` als Ganzzahl 0–100, `direction` ∈ {forward, backward, stop}. Mindestens ein Feld muss gesetzt sein, unbekannte Felder werden abgelehnt.
- `:id` wird als positive Ganzzahl geprüft.
- Tests für jede Regel, einschließlich `speed: 500`, `speed: 1.5` und `direction: "sideways"`.

### PR 1.5 *(nur wenn E1 = behalten)*: Zustand pro Zug, DB als einzige Wahrheit (~200 Zeilen)

- Die globale `service`-Instanz entfällt. Zustand und Geschwindigkeit stehen ausschließlich in der DB, die Übergänge prüft eine reine Funktion `applyCommand(train, cmd) → train | Fehler`.
- `stop` setzt `speed = 0` und `direction = 'stop'`. Ohne `action` bleibt `isActive` unverändert.
- `/health` meldet nur noch `{ok: true}`. Der Zustand der Züge kommt über `/api/trains`.
- `xstate` und `trainMachine.ts` werden entfernt.

### PR 1.6: GPIO-Lebenszyklus und geordneter Shutdown (~140 Zeilen)

- `gpio.init()` wird **einmal** beim Start aufgerufen, die Pins werden beim Start als Ausgang konfiguriert (nicht mehr im Request-Handler).
- Der fest einprogrammierte Pin 17 wird zur Konfiguration `TRAIN_POWER_PIN` (Standard 17). Entfällt bei E1 = entfernen später ohnehin.
- `src/shutdown.ts`: `shutdown(reason)`
  - idempotent
  - Reihenfolge: HTTP-Server schließen (`server.close`), WebSocket-Clients schließen, GPIOs auf Standardwerte setzen und freigeben, `prisma.$disconnect()`
  - Timeout von 5 s, danach `process.exit(1)`
- Behandelt `SIGINT` **und** `SIGTERM` (systemd).
- Tests: `shutdown` ruft alle Schritte in dieser Reihenfolge auf und läuft auch bei doppeltem Aufruf nur einmal.

### PR 1.7 *(nur wenn E1 = behalten)*: WebSocket korrigieren (~170 Zeilen)

- Nachrichten werden mit zod validiert (`{type: 'command', payload: {trainId, ...TrainCommand}}`) und laufen über denselben Service wie REST.
- Ein Ereignisbus (`EventEmitter`) sendet jede Zustandsänderung an alle verbundenen Clients, auch wenn sie über REST ausgelöst wurde.
- `ws.on('error')` wird behandelt. Ein Heartbeat (Ping/Pong, 30 s) räumt tote Verbindungen ab.

### PR 1.8: Aufräumen und Dokumentation (~80 Zeilen)

- Ungenutztes entfernen: `src/types.ts`, Modell `Route`, `createGpio`, `config.databaseUrl`.
- Skript `prisma:migrate`: Name nicht mehr fest auf `init` setzen (`prisma migrate dev`).
- README: Abschnitt „Bekannte Probleme“ aktualisieren.

**Ende Phase 1:** Der Prototyp ist stabil, getestet, baut und fährt sauber herunter. Er steuert aber weiterhin keine Hardware.

---

## Phase 2: Portierung des Python-Servers

### Zielarchitektur

```
src/
├── server.ts                 Bootstrap (Konfiguration, DB, GPIO, Registry, HTTP, Signale)
├── app.ts                    createApp(deps), Routen registrieren
├── config.ts                 PORT=5000, GPIO_DRIVER, GPIO_CHIP, DATABASE_URL, LOG_LEVEL
├── shutdown.ts
├── http/                     errors.ts, validate.ts, auth.ts
├── gpio/
│   ├── driver.ts             Interface GpioDriver
│   ├── mockDriver.ts
│   ├── libgpiodDriver.ts
│   └── index.ts              Factory nach GPIO_DRIVER (mock | libgpiod)
├── auth/werkzeugHash.ts      Passwort-Hashes im werkzeug-Format prüfen und erzeugen
├── domain/
│   ├── relais.ts             Relais, SwitchPoint, StopPoint
│   └── switchTypes.ts
├── services/
│   ├── relaisRegistry.ts     Ersatz für gpioservice.py
│   ├── pinValidator.ts
│   ├── configService.ts
│   └── programRunner.ts      Ersatz für programMachine.py
├── actions/                  setSwitch.ts, setStop.ts, waitFor.ts, startAtClock.ts, index.ts
├── device/                   deviceController.ts, stateLed.ts, powerButton.ts
├── routes/                   info.ts, switches.ts, stops.ts, config.ts, programs.ts, control.ts, device.ts
├── validation/schemas.ts     zod-Nachbau von schemes/*.json
└── cli/                      createUser.ts, importLegacy.ts, gpioTest.ts
```

**Abbildung Python → Node**

| Python | Node |
|---|---|
| `gpioservice.py` | `services/relaisRegistry.ts` |
| `models/GPIORelaisModel.py` | `domain/relais.ts` |
| `databaseControllerModule.py` | Prisma (`prisma/schema.prisma`) |
| `programMachine.py`, `programController.py` | `services/programRunner.ts` |
| `actions/*.py` | `actions/*.ts` |
| `*ApiController.py` | `routes/*.ts` |
| `authentication.py` | `http/auth.ts` + `auth/werkzeugHash.ts` |
| `stateControllerModule.py` | `device/stateLed.ts` |
| `powerControllerModule.py` | `device/powerButton.ts` |
| `deviceController.py` | `device/deviceController.ts` |
| `validators/*`, `schemes/*.json` | `validation/schemas.ts`, `services/pinValidator.ts` |
| `trainmote.py` (Erst-Benutzer, `--autostart`) | `cli/createUser.ts`, systemd-Unit |
| `configControllerModule.py` (INI-Datei) | `.env` |
| `bluetoothservice.py` | **nicht portiert** (wird vom Einstiegspunkt nicht verwendet) |
| `traintrackingservice.py` | **nicht portiert** (die Messschleife im Original ist auskommentiert, d. h. sie tut nichts). `mess_id` wird nur gespeichert. |
| `libInstaller.py`, `scripts/updateScript.sh` | entfällt bzw. in PR 2.18 ersetzt |

**Python-Fehler, die bewusst nicht übernommen werden** (Liste in `docs/KOMPATIBILITAET.md`):

- SQL-Injection: entfällt durch Prisma.
- `ClockAction` liest die Sekunden aus `inputs[1]` statt `inputs[2]`.
- `cancelAction` ruft `join()` vor `kill.set()` auf und blockiert dadurch.
- Pins werden mit `is` statt `==` verglichen.
- Ein Programm lässt sich nur im Zustand `runningAction` abbrechen.
- `GET /stoppoint/<id>` antwortet bei unbekannter ID mit 200 und einer Fehlermeldung (künftig 404).
- `GET /program/<id>` stürzt bei unbekannter ID ab (künftig 404).

### Abhängigkeitsgraph

```
Phase 1:  1.1 → 1.2 → 1.3 → 1.4 → 1.6 → 1.8

Phase 2:  2.1 → 2.2 ─┬─→ 2.3 (Hardware, parallel möglich)
                     │
          2.4 ───────┼─→ 2.5a → 2.5b ─┐
                     │                │
                     └─→ 2.6 → 2.7a → 2.7b → 2.8 (braucht auch 2.5b)
                                              │
            ┌───────────────┬─────────────────┼─────────────────┐
            ▼               ▼                 ▼                 ▼
           2.9            2.10              2.11              2.12
                                              │                 │
                                              ▼                 ▼
                                            2.15    2.13a → 2.13b → 2.14
                                              │
                                              ▼
                                            2.16

          2.17 (nach 2.4, 2.5a)    2.18 (nach 2.16)    2.19 (nach 2.13b)
          2.20 zuletzt, wenn alles andere gemergt ist
```

- Phase 2 beginnt erst, wenn Phase 1 abgeschlossen ist.
- Nach 2.8 sind die vier Stränge Weichen (2.9), Haltepunkte (2.10), Konfiguration (2.11 → 2.15 → 2.16) und Programme (2.12 → 2.13a → 2.13b → 2.14) unabhängig voneinander.
- 2.3 braucht nur 2.2 und kann parallel zur Software-Arbeit auf dem Pi laufen.

---

### PR 2.1: Grundgerüst und Konfiguration (~150 Zeilen)

- `config.ts` mit zod-validierter Umgebung:
  - `PORT` (Standard **5000**, siehe E2)
  - `GPIO_DRIVER` (`mock` | `libgpiod`, Standard `mock` außerhalb von Linux/ARM)
  - `GPIO_CHIP` (optional)
  - `DATABASE_URL`
  - `LOG_LEVEL`
  - Ungültige Konfiguration bricht den Start mit einer klaren Meldung ab.
- Kleiner Logger `src/log.ts` (Level, Zeitstempel, `console` darunter). Er ersetzt die verstreuten `console.log`-Aufrufe.
- Die Ordnerstruktur laut Zielarchitektur wird angelegt, soweit Code verschoben wird (`http/errors.ts` usw. aus Phase 1).
- `.env.example` aktualisieren.

### PR 2.2: GPIO-Treiberschnittstelle und Mock (~200 Zeilen)

```ts
export interface GpioDriver {
  setupOutput(pin: number, initial: 0 | 1): void;
  setupInput(pin: number, opts?: { pull?: 'up' | 'down' | 'none' }): void;
  write(pin: number, value: 0 | 1): void;
  read(pin: number): 0 | 1;        // liefert bei Ausgängen den zuletzt geschriebenen Wert
  release(pin: number): void;      // entspricht GPIO.cleanup(pin)
  close(): void;                   // alle Pins freigeben
}
```

- Das Interface ersetzt `lib/gpio.ts` aus dem Prototyp.
- `MockDriver` speichert Zustand und Modus pro Pin, wirft bei `write` auf einen nicht eingerichteten Pin und protokolliert alle Schreibvorgänge mit Zeitstempel. Die Tests prüfen damit z. B. die Pulsfolge des Weichenstroms.
- `gpio/index.ts`: Factory anhand von `config.GPIO_DRIVER`.
- Unit-Tests für den Mock.

### PR 2.3: Echter GPIO-Treiber (libgpiod) inklusive Spike (~220 Zeilen)

**Spike vorab (halber Tag, Ergebnis im PR):** `node-libgpiod` auf Pi 4 und Pi 5 mit Raspberry Pi OS Bookworm 64-bit testen.

- Prüfen: Build auf Node 22, Ausgang setzen, Eingang lesen, Freigabe beim Prozessende.
- Fallback, falls das nicht funktioniert: `opengpio`.
- Vorbedingung auf dem Pi: `sudo apt install libgpiod-dev build-essential`.

Umsetzung:

- `LibgpiodDriver`:
  - **Chip-Erkennung über das Label:** `pinctrl-rp1` auf dem Pi 5, `pinctrl-bcm2711` bzw. `pinctrl-bcm2835` auf Pi 4 und älter. Der Gerätename (`gpiochip0` oder `gpiochip4`) unterscheidet sich je nach Kernelversion; `GPIO_CHIP` überschreibt die Erkennung.
  - Die Line-Offsets entsprechen den BCM-Nummern, wie im Python-Code (`GPIO.BCM`).
  - Den Zustand von Ausgängen merkt sich der Treiber selbst. Python hat dafür `GPIO.input` auf Ausgangspins gelesen.
- Die Bibliothek wird als `optionalDependencies` eingebunden, damit `npm install` unter macOS weiter funktioniert. Die Factory lädt sie per dynamischem `import()` und gibt eine klare Fehlermeldung aus, wenn sie fehlt.
- `cli/gpioTest.ts` (`npm run gpio:test -- <pin>`) schaltet einen Pin 3× im Sekundentakt um, für die Prüfung an der Hardware.
- **Hardware-Checkliste:** Relais an Pin X klickt; nach `Ctrl+C` ist der Pin freigegeben; nach dem Start eines zweiten Prozesses meldet dieser „Pin belegt“.

### PR 2.4: Datenbankschema für die Domäne (~130 Zeilen + generierte Migration)

- Neue Modelle mit denselben Feldnamen wie in Python (Kompatibilität der JSON-Antworten):
  - `Switch`: `id`, `uid` (unique, UUID), `relais_id` (unique), `switchType`, `defaultValue`, `needsPowerOn`, `name`, `description`, `created`, `updated`
  - `Stop`: `id`, `uid`, `relais_id` (unique), `mess_id?`, `defaultValue`, `name`, `description`, …
  - `Config`: Singleton mit `id = 0`, `switchPowerRelais?`, `powerRelais?`, `stateRelais?`, `deviceName?`
  - `Program`: `id`, `uid`, `name`, Relation `actions`
  - `Action`: `id`, `uid`, `programId` (Fremdschlüssel mit `onDelete: Cascade`), `type`, `position`, `inputs` (JSON-String), `name`
  - `User`: `id`, `uid`, `username` (unique), `password`, `roles`
- Unique-Constraints auf `relais_id` verhindern doppelte Belegung zusätzlich in der DB. Die Prüfung über Tabellengrenzen hinweg übernimmt der Pin-Validator.
- Ab hier gibt es echte Migrationen: `prisma/migrations/` wird committet, auf dem Pi läuft `prisma migrate deploy`.
- Bei E1 = entfernen bleiben die Modelle `Train` und `Route` bis PR 2.8 bestehen; die Löschung erfolgt dort.

### PR 2.5a: Passwort-Hashes im werkzeug-Format (~180 Zeilen)

**Ziel:** Bestehende Benutzer der Python-Version können sich nach dem Import mit ihrem bisherigen Passwort anmelden.

- `verifyWerkzeugHash(hash, password)`:
  - `pbkdf2:sha256:<iter>$<salt>$<hex>`: `crypto.pbkdf2` mit dem Salt als UTF-8-String
  - `scrypt:<N>:<r>:<p>$<salt>$<hex>`: `crypto.scrypt` mit `keylen 64` und `maxmem` mindestens `128·N·r·2`. Der Node-Standardwert (32 MB) reicht für N=32768 nicht.
  - Vergleich mit `crypto.timingSafeEqual`
- `createWerkzeugHash(password)` erzeugt `scrypt:32768:8:1$...`. Damit bleiben neue Hashes auch für die Python-Version lesbar.
- **Tests mit echten Vektoren:** einmalig mit Python erzeugen (`werkzeug.security.generate_password_hash` für pbkdf2 und scrypt) und als Konstanten einchecken.

### PR 2.5b: Basic-Auth-Middleware und Benutzer-CLI (~200 Zeilen)

- `http/auth.ts`: `requireAuth({ role?: 'admin' })`.
  - Parst den `Authorization: Basic`-Header und lädt den Benutzer per `username`, statt wie Python alle Benutzer zu laden.
  - Ohne bzw. mit falschen Daten: 401 mit `WWW-Authenticate: Basic realm="Trainmote"`. Mit falscher Rolle: 403.
- Einfacher Schutz gegen Brute-Force: Zähler pro IP im Speicher, nach 10 Fehlversuchen 60 s Sperre.
- `cli/createUser.ts` (`npm run user:create`): fragt interaktiv Benutzername und Passwort ab (Passwort zweimal). Dies ersetzt die Abfrage beim Start in `trainmote.py`, weil systemd kein Terminal hat.
- Beim Serverstart ohne Benutzer erscheint eine Warnung im Log mit Hinweis auf `npm run user:create`.
- Tests: 401, 403, 200, Sperre.

### PR 2.6: Validierungsschemas und Pin-Validator (~240 Zeilen)

- `validation/schemas.ts`: zod-Nachbau von `switch_scheme`, `switch_update_scheme`, `stop_scheme`, `stop_update_scheme`, `config_scheme`, `program_scheme`, `program_update_scheme`.
- Zusätzliche Prüfungen, die Python nur verstreut gemacht hat:
  - `switchType` ∈ {`TM_SWITCH_STRAIGHT_LEFT`, `TM_SWITCH_STRAIGHT_RIGHT`, `TM_SWITCH_BORN_LEFT`, `TM_SWITCH_BORN_RIGHT`, `TM_SWITCH_CROSS`}
  - `defaultValue` ∈ {0, 1}
  - Action-`type` ∈ {`SetSwitch`, `SetStop`, `WaitFor`, `StartAtClock`} mit passender Anzahl von `inputs` je Typ
- `services/pinValidator.ts`:
  - `isValidGpio(pin)`: BCM 2–27, wie `validGpios` in Python
  - `assertPinFree(pin, { exceptUid? })`: prüft Weichen, Haltepunkte und alle drei Konfigurations-Relais mit `===` und wirft 409 mit derselben Meldung wie Python
- Tests für alle Schemas und alle Konfliktfälle.

### PR 2.7a: Domänenmodelle der Relais (~200 Zeilen)

- `Relais` (Basisklasse): `uid`, `relais_id`, `defaultValue`, `name`, `description`. Methoden `status()`, `set(v)`, `toDefault()`, `toJSON()`. Das JSON hat dasselbe Format wie `to_dict()` in Python, einschließlich `status`.
- `StopPoint extends Relais`: zusätzlich `mess_id`.
- `SwitchPoint extends Relais`: zusätzlich `switchType`, `needsPowerOn`, `powerRelais?`.
  - `async set(v)` bildet die Pulsfolge aus Python nach: Weichenstrom-Relais LOW, Pin setzen, **200 ms warten**, Weichenstrom-Relais HIGH.
  - **Neu:** Ein gemeinsamer Mutex für das Weichenstrom-Relais serialisiert parallele Weichenstellungen. In Python konnten sich zwei gleichzeitige Requests den Strom gegenseitig abschalten.
- Tests gegen das Protokoll des Mock-Treibers: korrekte Reihenfolge und Zeitabstände (mit `vi.useFakeTimers`), zwei parallele Weichen werden nacheinander geschaltet.

### PR 2.7b: Relais-Registry (~220 Zeilen)

Ersatz für `gpioservice.py`:

- `load()`: Konfiguration lesen. Ist ein Weichenstrom-Relais konfiguriert, wird es eingerichtet (initial HIGH). Danach alle Weichen und Haltepunkte aus der DB einrichten (initial `defaultValue`).
- `add(relais)`, `remove(uid)` (inklusive `driver.release`), `replace(old, new)` bei Pinwechsel.
- `setValue(uid, value?)`: ohne `value` wird umgeschaltet, wie `switchPin` in Python. Gibt `{ model, currentValue }` zurück.
- `rebindSwitchPower(pin | null)`: nach einer Konfigurationsänderung.
- `allToDefault()` und `close()` für den Shutdown (wird in `shutdown.ts` eingehängt).
- Fehlerhafte Pins (z. B. belegt) lassen den Start nicht scheitern. Sie werden geloggt und als `status: null` gemeldet; Python hat solche Pins nur ausgegeben und übersprungen.
- Tests: Laden aus der Test-DB, Umschalten, Entfernen gibt den Pin frei, Neubindung des Weichenstroms.

### PR 2.8: API-Grundlage, Info-Endpunkt, Prototyp entfernen (~120 Zeilen + Löschungen)

- `routes/info.ts`: `GET /trainmote/api/v1` liefert `{trainmote, version, name}`. `name` ist `deviceName` aus der Konfiguration, sonst `os.hostname()`.
- `server.ts`: Bootstrap mit Treiber → Registry → App. Bei E1 = entfernen werden `/api/trains`, `trainMachine.ts`, `xstate` und die Modelle `Train`/`Route` gelöscht (mit Migration).
- `docs/KOMPATIBILITAET.md` wird angelegt (Abweichungen von Python, siehe oben).
- Contract-Tests: JSON-Struktur der Antworten gegen fest eingecheckte Beispiele im Python-Format.

### PR 2.9: Weichen-API (~260 Zeilen)

| Methode | Pfad | Auth | Antwort |
|---|---|---|---|
| GET | `/trainmote/api/v1/switch/all` | – | 200, Liste |
| GET | `/trainmote/api/v1/switch/:id` | – | 200 / 404 |
| POST | `/trainmote/api/v1/switch` | admin | 201 / 400 / 409 |
| PATCH | `/trainmote/api/v1/switch/:id` | admin | 200 / 404 / 409 |
| DELETE | `/trainmote/api/v1/switch/:id` | admin | 205 / 404 |
| PATCH | `/trainmote/api/v1/control/switch/:id` | – | 200 `{model, currentValue}` / 400 |

- Jede Änderung erfolgt in der DB und in der Registry. **Neu:** Beim Löschen wird auch das Relais in der Registry entfernt und der Pin freigegeben; Python hat nur die DB-Zeile gelöscht.
- Die Auth-Regeln entsprechen exakt Python (Steuerung ohne Login). Ob die Steuerung künftig einen Login verlangen soll, ist eine offene Frage für die App und steht in `KOMPATIBILITAET.md`.
- Tests für alle Statuscodes.

### PR 2.10: Haltepunkt-API (~230 Zeilen)

- Gleiche Struktur wie 2.9 unter `/stoppoint` und `/control/stoppoint/:id`.
- Gemeinsame Teile aus 2.9 (Laden-oder-404, Pin-Prüfung bei Änderung) kommen in einen Helfer `routes/relaisRoutes.ts`, damit dieser PR klein bleibt.
- Tests.

### PR 2.11: Konfigurations-API (~200 Zeilen)

- `GET /trainmote/api/v1/config` (admin): 200 oder 404.
- `POST /trainmote/api/v1/config` (admin): 201.
  - Prüft die Konfliktregeln der drei Relais-Pins gegen Weichen und Haltepunkte (409).
  - Speichert die Konfiguration (Upsert mit `id = 0`).
  - Danach `registry.rebindSwitchPower(...)` sowie Neustart von Status-LED und Abschalt-Taster über `configService.onChange` (Implementierung in 2.15, hier zunächst ein Ereignis ohne Empfänger).
- Ein Wert von `0` bedeutet wie in Python „nicht gesetzt“ und wird als `null` gespeichert.

### PR 2.12: Programm-API (CRUD) (~260 Zeilen)

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/trainmote/api/v1/program` | admin |
| GET | `/trainmote/api/v1/program/all` | – |
| GET | `/trainmote/api/v1/program/:id` | – |
| PATCH | `/trainmote/api/v1/program/:id` | admin |
| DELETE | `/trainmote/api/v1/program/:id` | admin |

- Anlegen und Ändern laufen in einer **Transaktion** (`prisma.$transaction`): Programm, Aktionen anlegen, `actionsToDelete` löschen, vorhandene Aktionen per `uid` aktualisieren.
- Aktionen werden immer nach `position` sortiert ausgeliefert.
- Läuft das Programm gerade: PATCH liefert 409, DELETE stoppt es zuerst (wie Python). Die Prüfung „läuft gerade“ ist bis 2.13b ein Stub.

### PR 2.13a: Aktionen (~220 Zeilen)

```ts
interface ProgramAction {
  prepare(): void;                         // wirft bei ungültigen inputs
  run(signal: AbortSignal): Promise<void>; // endet bei Abbruch mit AbortError
}
```

| Typ | `inputs` | Verhalten |
|---|---|---|
| `SetSwitch` | `[uid, "0"/"1"]` | `registry.setValue`, Fehler werden geloggt und die Aktion endet trotzdem (wie Python) |
| `SetStop` | `[uid, "0"/"1"]` | wie `SetSwitch` |
| `WaitFor` | `[hh, mm, ss]` | abbrechbares `setTimeout` |
| `StartAtClock` | `[hh, mm, ss]` | wartet bis zur Uhrzeit (heute, sonst morgen), **mit korrekten Sekunden aus `inputs[2]`**; abbrechbar |

- Tests mit Fake-Timern: Wartezeiten, Abbruch, Zeitpunkt über Mitternacht.

### PR 2.13b: ProgramRunner (~180 Zeilen)

- `start(program)`: wirft 409, wenn schon ein Programm läuft. Danach eine asynchrone Schleife über die Aktionen; der `AbortController` wird gespeichert.
- `cancel()`: in jedem Zustand möglich (Python erlaubte das nur während einer laufenden Aktion).
- `status()` liefert `{ runningProgram, currentAction, followingActions }`, wie der Status-Endpunkt in Python.
- Ein Fehler in einer Aktion beendet das Programm und wird geloggt. Er stürzt den Prozess nicht ab.
- Ereignisse (`actionStarted`, `programEnded`) über einen `EventEmitter`, für Logs und optional WebSocket (2.19).
- Tests: kompletter Durchlauf mit mehreren Aktionen, Abbruch während `WaitFor`, zweiter Start liefert 409.

### PR 2.14: Programmsteuerung und Status-Endpunkt (~150 Zeilen)

- `PATCH /trainmote/api/v1/control/program/start/:id` (admin): 200, 404 oder 409.
- `PATCH /trainmote/api/v1/control/program/stop/:id` (admin): 204 oder 404.
- `GET /trainmote/api/v1/control/program/status`: Programm oder `[]` (wie Python).
- `GET /trainmote/api/v1/status` (admin): Info-Daten plus `runningProgram`, `currentAction`, `followingActions`.
- Der Stub aus 2.12 wird durch den echten Runner ersetzt.

### PR 2.15: Status-LED und Abschalt-Taster (~200 Zeilen)

- `device/stateLed.ts`: Zustände `NOT_CONNECTED` (Blinken 1 s), `CONNECTED` (an), `SHUTDOWN` (Blinken 0,2 s). Umsetzung mit `setInterval` statt Threads; aktiv LOW wie in Python.
- `device/deviceController.ts` (Grundversion): `poweroff()` führt nach dem Aufräumen über `shutdown()` per `execFile` (ohne Shell) `systemctl poweroff` aus. Mit `DEVICE_DRY_RUN=1` wird nur protokolliert, statt auszuführen (für Entwicklung und Tests). PR 2.16 erweitert die Datei.
- `device/powerButton.ts`: Eingang im 500-ms-Takt abfragen. Bei HIGH → `deviceController.poweroff()`. Entprellung: Der Pegel muss 2 Abfragen hintereinander anliegen. Python hat sofort ausgelöst.
- Beide reagieren auf `configService.onChange` (aus 2.11) und werden in `shutdown.ts` beendet.
- Ein Aufruf des Info- oder Status-Endpunkts setzt die LED auf `CONNECTED`, wie in Python.
- **Hardware-Checkliste:** LED blinkt nach dem Start; nach einem Aufruf der App leuchtet sie dauerhaft; der Taster fährt den Pi herunter (zuerst mit `DEVICE_DRY_RUN=1` prüfen).

### PR 2.16: Geräte-API (~170 Zeilen)

- `POST /trainmote/api/v1/device/restart`, `/shutdown`, `/update` (admin).
- `deviceController.ts` (aus 2.15) wird um `reboot()` (`systemctl reboot`) erweitert. Die Endpunkte lösen die Aktion nach 2 s aus, damit die HTTP-Antwort noch beim Client ankommt.
- **Rechte:** Der Dienst läuft nicht als root. Eine Polkit-Regel bzw. ein `sudoers`-Eintrag für genau diese zwei Befehle wird in 2.18 durch das Installationsskript angelegt. Fehlen die Rechte, antwortet der Endpunkt mit 403 und einem klaren Hinweis (Python hat dafür 401 verwendet).
- `/update` führt `scripts/update.sh` aus (`git pull`, `npm ci`, `npm run build`, `prisma migrate deploy`) und startet danach `systemctl restart trainmote`. Das Ergebnis wird ins Log geschrieben.

### PR 2.17: Import der Python-Datenbank (~200 Zeilen)

- `npm run import:legacy -- /content/tom-db.sqlite`
- Ein zweiter `PrismaClient` mit `datasourceUrl` auf die alte Datei liest per `$queryRaw`. Dafür ist keine zusätzliche Abhängigkeit nötig.
- Übernimmt `TMSwitchModel`, `TMStopModel`, `TMConfigModel`, `TMProgramModel`, `TMActionModel` (falls vorhanden; ab Python-Version 0.5.0) und `TMUser`. Die **`uid`s bleiben erhalten**, damit gespeicherte IDs in der App weiter gültig sind. Die Passwort-Hashes werden unverändert übernommen (dank 2.5a).
- Einstellungen:
  - Ohne `--force` bricht das Skript ab, wenn die Ziel-DB nicht leer ist.
  - `--dry-run` gibt nur eine Zusammenfassung aus.
- Tests mit einer kleinen alten DB als Fixture, angelegt mit dem `CREATE TABLE`-SQL aus `databaseControllerModule.py`.

### PR 2.18: Deployment auf dem Pi (~220 Zeilen)

- `deploy/trainmote.service`: systemd-Unit mit `User=trainmote`, `SupplementaryGroups=gpio`, `Restart=on-failure`, `EnvironmentFile`.
- `deploy/install.sh`:
  - Benutzer und Gruppen anlegen
  - Rechte für `reboot` und `poweroff` einrichten
  - `npm ci && npm run build && npx prisma migrate deploy`
  - Unit installieren und aktivieren
  - erkannte alte Python-DB zum Import anbieten
  - `npm run user:create` aufrufen, falls noch kein Benutzer existiert
- Ersatz für `trainmote --autostart` aus Python. Keine Änderungen mehr an `/etc/rc.local`.
- **Hardware-Checkliste:** Neuinstallation auf frischem Raspberry Pi OS; Neustart startet den Dienst; `systemctl stop` setzt alle Relais auf ihre Standardwerte zurück.

### PR 2.19 *(optional)*: WebSocket für Live-Status (~180 Zeilen)

- Das Python-Original hatte keinen WebSocket. Er bleibt nur, wenn die App ihn nutzen soll.
- `ws://<pi>:5000/trainmote/api/v1/ws`. Authentifizierung über Basic Auth im Upgrade-Request.
- Sendet `relaisChanged`, `programStarted`, `actionStarted`, `programEnded` aus den Ereignisbussen von Registry und Runner.

### PR 2.20: Abschluss (reine Löschung + ~150 Zeilen Dokumentation)

- README vollständig neu: Installation über `install.sh`, alle Endpunkte, Migration von Python.
- Python-Code (`src/pkg_trainmote`, `setup.py`, `python-publish.yml`) entfernen, **erst nachdem** die Node-Version mindestens zwei Wochen auf echter Hardware gelaufen ist. Die Löschung ist ein eigener Commit und zählt nicht zum Limit.
- Optional `npm/` ins Wurzelverzeichnis verschieben (reine Verschiebung, `git mv`).
- `.github/copilot-instructions.md` auf die Node-Architektur aktualisieren.

---

## Übersicht

| PR | Inhalt | Zeilen (Schätzung) | Hardware-Test |
|---|---|---|---|
| 1.1 | Build, Tooling, CI, Größen-Check | ~90 | |
| 1.2 | Tests, `createApp` | ~220 | |
| 1.3 | Fehlerbehandlung, Express 5 | ~150 | |
| 1.4 | Validierung | ~170 | |
| 1.5 | *nur E1 = behalten:* Zustand pro Zug | ~200 | |
| 1.6 | Shutdown, GPIO-Lebenszyklus | ~140 | |
| 1.7 | *nur E1 = behalten:* WebSocket | ~170 | |
| 1.8 | Aufräumen | ~80 | |
| 2.1 | Gerüst, Konfiguration, Logger | ~150 | |
| 2.2 | GPIO-Interface, Mock | ~200 | |
| 2.3 | libgpiod-Treiber (+ Spike) | ~220 | ✔ |
| 2.4 | Prisma-Schema | ~130 | |
| 2.5a | werkzeug-Hashes | ~180 | |
| 2.5b | Basic Auth, Benutzer-CLI | ~200 | |
| 2.6 | Schemas, Pin-Validator | ~240 | |
| 2.7a | Relais-Modelle | ~200 | |
| 2.7b | Relais-Registry | ~220 | ✔ |
| 2.8 | Info-Endpunkt, Prototyp entfernen | ~120 | |
| 2.9 | Weichen-API | ~260 | ✔ |
| 2.10 | Haltepunkt-API | ~230 | ✔ |
| 2.11 | Konfigurations-API | ~200 | |
| 2.12 | Programm-CRUD | ~260 | |
| 2.13a | Aktionen | ~220 | |
| 2.13b | ProgramRunner | ~180 | |
| 2.14 | Programmsteuerung, Status | ~150 | ✔ |
| 2.15 | Status-LED, Taster | ~200 | ✔ |
| 2.16 | Geräte-API | ~170 | ✔ |
| 2.17 | Import der Python-DB | ~200 | |
| 2.18 | Deployment | ~220 | ✔ |
| 2.19 | *optional:* WebSocket | ~180 | |
| 2.20 | Abschluss, Python entfernen | ~150 | |

Mit der Empfehlung zu E1 sind das **29 PRs** (6 in Phase 1 ohne 1.5 und 1.7, 23 in Phase 2), bzw. 28 ohne die optionale 2.19.

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| `node-libgpiod` baut nicht auf dem Ziel-Pi bzw. der Node-Version | Spike zu Beginn von 2.3, Fallback `opengpio`. Das Treiber-Interface (2.2) isoliert den Rest des Codes davon. |
| Unterschiedliche GPIO-Chip-Namen (Pi 4 / Pi 5 / Kernelversion) | Erkennung über das Label, Übersteuerung mit `GPIO_CHIP` |
| Prisma-Engines auf 32-bit Raspberry Pi OS | 64-bit OS als Voraussetzung in der README. Vor 2.4 einmal `prisma migrate deploy` auf dem Ziel-Pi ausführen. |
| Die App hängt von nicht dokumentiertem Python-Verhalten ab | Contract-Tests (2.8), Abweichungen in `KOMPATIBILITAET.md`. Vor 2.20 einen Testlauf mit der echten App durchführen. |
| Relais schalten beim Start kurz falsch (Initialwerte) | Ausgänge werden direkt mit `initial = defaultValue` angefordert (2.7b), nicht erst eingerichtet und danach geschrieben. Wird in der Hardware-Checkliste von 2.7b geprüft. |

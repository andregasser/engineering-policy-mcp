# Engineering Policy MCP
## Konzept- und Implementierungsgrundlage

**Status:** Draft v0.3  
**Zielzeitraum:** 4–5 Wochen  
**Plattform-Implementierung:** Python  
**Primäre Zielprojekte:** Java, optional Kotlin  
**Primäre Hosts:** Claude Code und Codex  
**Betriebsform im MVP:** lokaler MCP-Server über `stdio`

---

## 1. Vision

Der Engineering Policy MCP stellt Coding Agents situationsabhängig jene Engineering Policies bereit, die für eine konkrete Entwicklungsaufgabe gelten.

Die Plattform wird in Python implementiert. Der Code, den die Plattform analysiert, stammt primär aus Java- und teilweise Kotlin-Projekten.

Der Server ersetzt weder CI noch Linter, Architekturtests oder bestehende Agent-Instruktionen. Er ergänzt diese durch eine gemeinsame, agentenunabhängige Policy-Auflösung:

```text
Java-/Kotlin-Repository + aktueller Arbeitskontext
                         │
                         ▼
                Analyzer erzeugen Facts
                         │
                         ▼
                 Policy Resolver wählt
                 relevante Policies aus
                         │
                         ▼
                  Claude Code / Codex
                  richtet Arbeit danach aus
```

Beispiele:

- Vor einem Commit erhält der Agent die Firmenregel für Conventional Commits.
- Vor Abschluss eines grösseren Changes erhält er die Pflicht, einen umfassenden Review durchzuführen.
- Bei Änderungen an OpenAPI-Dateien erhält er die produktspezifische Kompatibilitätsregel.
- Bei Änderungen an Flyway- oder Liquibase-Migrationen erhält er relevante Migrations- und Rollback-Anweisungen.

Das Projekt ist zugleich ein Lernlabor für MCP, Tool Selection, Context Engineering, Agent-Verhalten, Plugin-Architekturen und Telemetrie.

---

## 2. Problemstellung

In einer Organisation verwenden Entwickler zunehmend unterschiedliche Coding Agents. Ohne gemeinsame Leitplanken entstehen mehrere Probleme:

- Standards werden in `AGENTS.md`, `CLAUDE.md`, Wikis und READMEs mehrfach gepflegt.
- Agenten erhalten je nach Host oder Repository unterschiedliche Regeln.
- Umfangreiche Instruktionsdateien belasten den Kontext, obwohl viele Regeln für die aktuelle Aufgabe irrelevant sind.
- Agents berücksichtigen Regeln nicht zuverlässig, wenn sie nur als statischer Text vorliegen.
- Company-, Team- und Produktregeln sind nicht zentral kombinierbar.
- Es fehlt eine gemeinsame Sicht darauf, welche Policies wann ausgewählt wurden.
- Die Organisation kann kaum messen, wie Agenten mit Engineering-Standards umgehen.

Der Engineering Policy MCP stellt einen gemeinsamen, host-neutralen Mechanismus bereit:

> Für den aktuellen Arbeitsschritt werden nur jene Policies ausgewählt, die aufgrund objektiver Engineering Facts relevant sind.

---

## 3. Nutzen

### 3.1 Nutzen für den Entwickler

- Claude Code und Codex erhalten dieselben Engineering-Regeln.
- Wiederkehrende Anweisungen müssen nicht ständig neu formuliert werden.
- Der Agent erinnert rechtzeitig an Reviews, Tests, API-Kompatibilität und Commit-Konventionen.
- Regeln werden passend zur tatsächlichen Änderung ausgewählt.
- Jede Policy enthält eine nachvollziehbare Begründung.
- Die Plattform kann im eigenen Java-/Kotlin-Alltag direkt eingesetzt werden.

### 3.2 Nutzen für AI-Karriere und Job-Sicherheit

Das Projekt vermittelt Fähigkeiten, die über reine Codegenerierung hinausgehen:

- Design und Implementierung von MCP-Servern
- Tool-Schema- und Tool-Description-Design
- Agenteninteraktion und Tool Selection
- Context Engineering
- Policy Resolution
- Plugin-Architekturen
- strukturierte, belegbare Tool-Antworten
- Telemetrie und Evaluation von Agentenverhalten
- Integration unterschiedlicher Coding-Agent-Hosts
- AI Governance im Software Engineering

Das Ziel ist nicht nur, einen MCP-Server schreiben zu können, sondern zu verstehen, wie Coding Agents mit externen Fähigkeiten und organisationsspezifischen Regeln zusammenarbeiten.

### 3.3 Nutzen für den Arbeitgeber

- einheitlichere Arbeitsweise über Teams und Agenten hinweg
- zentrale Pflege von Company-, Team- und Produktstandards
- weniger redundante Agent-Instruktionen
- frühzeitige Steuerung des Agenten, bevor CI-Checks scheitern
- bessere Nachvollziehbarkeit angewendeter Policies
- gemeinsame Basis für Java-, Kotlin- und später .NET-Produkte
- schrittweise messbare AI-Governance ohne grosses Plattformprojekt
- Wiederverwendung bestehender Tools und CI-Gates statt deren Neuerfindung

---

## 4. Ziele und Nicht-Ziele

### 4.1 Primäre Ziele

1. Einen lokal ausführbaren MCP-Server in Python implementieren.
2. Claude Code und Codex dieselben Policy-Tools anbieten.
3. Policies auf Company-, Team- und Produktebene kombinieren.
4. Engineering Facts durch Analyzer erzeugen.
5. Relevante Policies deterministisch auflösen.
6. Jede wichtige Engine-Entscheidung strukturiert protokollieren.
7. Das System in realen Java-Projekten einsetzen.
8. Den MVP in vier bis fünf Wochen abschliessen.

### 4.2 Nicht-Ziele des MVP

Der MVP ist ausdrücklich kein:

- universeller Repository Analyzer
- Java- oder Spring-Code-Understanding-System
- CI-Ersatz
- Linter-Ersatz
- vollständiges Enforcement-System
- zentrales Webportal
- Telemetrie-Dashboard
- Remote-MCP-Dienst
- LLM-basierter Policy Resolver
- allgemeine Policy-Programmiersprache
- vollwertiger Plugin-Marketplace

---

## 5. Leitprinzipien

### 5.1 Host-neutral

Die Policy-Logik kennt weder Claude Code noch Codex. Hostspezifische Konfiguration und Lifecycle-Anbindung befinden sich in dünnen Adaptern.

### 5.2 Deterministische Policy-Auswahl

Ein LLM entscheidet nicht, welche Policies gelten. Analyzer produzieren Facts; der Resolver wählt anhand klarer Regeln passende Policies.

### 5.3 Agent führt semantische Arbeit aus

Die Engine kann die Policy `comprehensive-review` auswählen. Den eigentlichen Review führt der Coding Agent durch.

### 5.4 Bestehende Werkzeuge wiederverwenden

Objektiv prüfbare Standards werden weiterhin durch bestehende Tools abgesichert:

- Git Hooks oder Commitlint
- Maven oder Gradle
- JUnit
- ArchUnit
- OpenAPI Diff
- Sonar
- CI

### 5.5 Explainability

Jede aufgelöste Policy enthält einen Grund:

```json
{
  "policyId": "company.comprehensive-review",
  "reason": "14 production files and 827 lines changed."
}
```

### 5.6 Telemetry First

Jede zentrale Entscheidung erzeugt ein kleines strukturiertes Telemetrie-Event. Telemetrie beeinflusst die Policy-Entscheidung nicht.

### 5.7 Read-only im MVP

Der MCP-Server verändert keine Dateien, erzeugt keine Commits und startet keine Deployments.

---

## 6. Begriffsmodell

### Policy

Eine Engineering-Anweisung, die unter bestimmten Bedingungen für einen Agentenlauf gilt.

Beispiele:

- Conventional Commits verwenden
- umfassenden Review durchführen
- öffentliche APIs abwärtskompatibel halten

### Fact

Eine objektive oder nachvollziehbar abgeleitete Aussage über Repository, Diff oder Arbeitskontext.

Beispiele:

- `change.production_files.count = 14`
- `change.lines.total = 827`
- `api.openapi.files_changed = true`
- `repository.build_system = gradle`
- `repository.language.java = true`

Facts besitzen Wert, Quelle, Confidence und Evidenz.

### Analyzer

Eine read-only Laufzeitkomponente, die Facts produziert.

Beispiele:

- `GitChangeAnalyzer`
- `RepositoryTechnologyAnalyzer`
- `OpenApiFileChangeAnalyzer`
- `ChangeSizeAnalyzer`

### Plugin

Ein installierbares Erweiterungspaket. Ein Plugin kann Analyzer und Policy Packs beitragen.

```text
Plugin
├── Analyzer
└── Policy Pack
```

Später können Plugins zusätzlich Verifier oder Context Sources bereitstellen.

### Policy Resolver

Komponente, die Policies anhand von Event, aktivierten Policy Sets und vorhandenen Facts auswählt.

### Policy Pack

Eine versionierte Sammlung zusammengehöriger Policies, zum Beispiel:

- `company-baseline`
- `java-backend`
- `dotnet-backend`
- `billing-product`

### Canonical Event

Ein host-neutraler fachlicher Zeitpunkt, zu dem Policies aufgelöst werden.

MVP:

- `task_start`
- `before_commit`
- `before_completion`

### Host Adapter

Übersetzt einen Lifecycle-Zeitpunkt von Claude Code oder Codex in ein kanonisches Policy Event.

---

## 7. Systemarchitektur

```text
┌───────────────────┐        ┌───────────────────┐
│    Claude Code    │        │       Codex       │
│ CLAUDE.md/Adapter │        │ AGENTS.md/Adapter │
└─────────┬─────────┘        └─────────┬─────────┘
          │ MCP                              │ MCP
          └──────────────┬───────────────────┘
                         ▼
              ┌────────────────────┐
              │ Engineering Policy │
              │ MCP Server         │
              └─────────┬──────────┘
                        ▼
              ┌────────────────────┐
              │ Application Layer  │
              │ resolve / explain  │
              └─────────┬──────────┘
                        ▼
       ┌────────────────┴────────────────┐
       ▼                                 ▼
┌───────────────┐                 ┌───────────────┐
│Analyzer Planner│                 │Policy Catalog │
└───────┬───────┘                 └───────┬───────┘
        ▼                                 ▼
┌───────────────┐                 ┌───────────────┐
│Analyzer       │                 │Policy Resolver│
│Registry       │                 └───────────────┘
└───────┬───────┘
        ▼
┌─────────────────────────────────────────┐
│ Facts: Git, Java/Kotlin, Maven/Gradle,  │
│ OpenAPI, Migration Paths                │
└─────────────────────────────────────────┘
```

---

## 8. Kanonische Policy Events

### 8.1 `task_start`

**Bedeutung:** Eine neue Benutzeraufgabe beginnt.

**Verfügbare Informationen:**

- Benutzerauftrag
- Repository-Pfad
- erkannter Technologie-Stack
- optional geplante Pfade
- noch kein verlässlicher finaler Diff

**Typische Policies:**

- allgemeine Testpflicht
- domänenspezifische Designregeln
- Hinweise auf sensible Bereiche
- Arbeitsabläufe, die früh berücksichtigt werden müssen

Die Auflösung kann vorläufig sein.

### 8.2 `before_commit`

**Bedeutung:** Der Agent möchte einen Commit erstellen.

**Technische Erkennung:** Ein hostspezifischer Adapter erkennt einen Commit-Versuch, zum Beispiel einen Shell-Aufruf mit `git commit`.

**Verfügbare Informationen:**

- Commit-Nachricht
- aktueller Diff
- geänderte Pfade
- Repository-Konfiguration

**Typische Policies:**

- Conventional Commits
- zulässige Commit-Typen
- Scope-Konventionen
- Verbot bestimmter Commit-Inhalte

### 8.3 `before_completion`

**Bedeutung:** Der Agent möchte die Aufgabe abschliessen.

**Verfügbare Informationen:**

- finaler oder nahezu finaler Arbeitsbaum
- geänderte Dateien
- Diff-Statistiken
- erkannte API- oder Migrationsänderungen

**Typische Policies:**

- umfassender Review
- relevante Tests
- API-Kompatibilitätsprüfung
- Rollback- oder Betriebsüberlegungen
- Abschlussbericht

---

## 9. Policy-Ebenen und Komposition

Policies werden in Policy Sets organisiert.

```text
Company Baseline
      +
Team-/Stack-Policy-Set
      +
Produkt-Policy-Set
      =
Effektive Policies
```

Beispiel:

```yaml
schema_version: 1

policy_sets:
  - company/baseline
  - teams/java-backend
  - products/billing
```

### Kompositionsregeln im MVP

1. Alle ausgewählten Sets werden vereinigt.
2. Policy-IDs müssen über alle Sets eindeutig sein.
3. Eine doppelte ID ist ein Konfigurationsfehler.
4. Overrides und Abschwächungen werden im MVP nicht unterstützt.
5. Produkte können zusätzliche strengere Policies hinzufügen.
6. Herkunft und Dateipfad werden in jeder Policy-Antwort ausgewiesen.

---

## 10. Policy-Format

Das YAML bleibt bewusst Konfiguration und wird nicht zu einer komplexen DSL.

### 10.1 Beispiel

```yaml
id: company.conventional-commits
title: Use Conventional Commits
severity: mandatory

events:
  - before_commit

instruction: >
  Use a Conventional Commit message.

when:
  facts:
    - fact: commit.requested
      operator: equals
      value: true

parameters:
  allowed_types:
    - feat
    - fix
    - refactor
    - test
    - docs
    - build
    - ci
    - chore
```

### 10.2 Felder

| Feld | Pflicht | Bedeutung |
|---|---:|---|
| `id` | ja | stabile, eindeutige Policy-ID |
| `title` | ja | kurzer Titel |
| `severity` | ja | `mandatory`, `recommended`, `advisory` |
| `events` | ja | kanonische Events |
| `instruction` | ja | Anweisung an den Coding Agent |
| `when` | nein | Fact-basierte Aktivierungsbedingungen |
| `parameters` | nein | strukturierte Zusatzdaten |
| `description` | nein | ausführlicher Hintergrund |
| `references` | nein | ADRs, Guidelines oder Dokumentation |

### 10.3 Operatoren im MVP

- `equals`
- `not_equals`
- `greater_than_or_equal`
- `less_than_or_equal`
- `contains`
- `matches`

Bedingungen werden im MVP als flache AND-Verknüpfung ausgewertet.

### 10.4 Beispiel: umfassender Review

```yaml
id: company.comprehensive-review
title: Perform a comprehensive review for substantial changes
severity: mandatory

events:
  - before_completion

instruction: >
  Perform a comprehensive review covering correctness, regressions,
  architecture consistency, security, backward compatibility,
  test coverage and unnecessary complexity. Resolve all material findings
  before completing the task.

when:
  facts:
    - fact: change.substantial
      operator: equals
      value: true

parameters:
  review_areas:
    - correctness
    - regression_risk
    - architecture
    - security
    - backward_compatibility
    - test_coverage
    - unnecessary_complexity
```

### 10.5 Beispiel: OpenAPI-Regel

```yaml
id: product.public-api-compatibility
title: Preserve public API compatibility
severity: mandatory

events:
  - before_completion

instruction: >
  Review the public API change for backward compatibility.
  Do not remove endpoints, required response properties, accepted values
  or status codes without an approved migration strategy.

when:
  facts:
    - fact: api.openapi.files_changed
      operator: equals
      value: true
```

---

## 11. Fact-Modell in Python

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class Evidence:
    source: str
    description: str
    path: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class Fact:
    key: str
    value: Any
    value_type: str
    confidence: Confidence
    producer_id: str
    evidence: tuple[Evidence, ...]
    observed_at: datetime
```

### Fact-Namenskonvention

```text
<domain>.<subject>.<property>
```

Beispiele:

```text
repository.language.java
repository.language.kotlin
repository.build_system
change.files.count
change.production_files.count
change.lines.added
change.lines.deleted
change.lines.total
change.substantial
api.openapi.files_changed
database.migration.files_changed
commit.requested
```

### Unknown-Semantik

Abwesenheit ist nicht automatisch `false`.

```python
@dataclass(frozen=True)
class FactPresent:
    fact: Fact


@dataclass(frozen=True)
class FactMissing:
    key: str


@dataclass(frozen=True)
class FactUnavailable:
    key: str
    reason: str
```

Kann ein Mandatory Fact nicht ermittelt werden, wird die Policy als `unresolved` ausgewiesen.

---

## 12. Analyzer-Modell

### 12.1 Python-Schnittstelle

```python
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class AnalyzerCost(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class AnalyzerDescriptor:
    id: str
    provides: frozenset[str]
    requires: frozenset[str]
    cost: AnalyzerCost
    plugin_id: str


@dataclass(frozen=True)
class AnalysisResult:
    facts: tuple[Fact, ...]
    warnings: tuple[str, ...] = ()


class Analyzer(Protocol):
    def descriptor(self) -> AnalyzerDescriptor:
        ...

    def supports(self, context: "RepositoryContext") -> bool:
        ...

    def analyze(
        self,
        context: "AnalysisContext",
        facts: "FactStore",
    ) -> AnalysisResult:
        ...
```

### 12.2 MVP-Analyzer

#### `RepositoryTechnologyAnalyzer`

Produziert:

```text
repository.language.java
repository.language.kotlin
repository.build_system
repository.framework.spring
```

Datenquellen:

- `.java`- und `.kt`-Dateien
- `pom.xml`
- `build.gradle`
- `build.gradle.kts`
- bekannte Maven-Dependencies und Gradle-Plugins

#### `GitChangeAnalyzer`

Produziert:

```text
change.files.count
change.lines.added
change.lines.deleted
change.lines.total
change.production_files.count
change.test_files.count
change.changed_paths
```

Datenquellen:

```bash
git diff
git diff --numstat
git status --porcelain
```

#### `ChangeSizeAnalyzer`

Benötigt:

```text
change.production_files.count
change.lines.total
```

Produziert:

```text
change.substantial
```

Thresholds stammen aus der Engine-Konfiguration.

#### `OpenApiFileChangeAnalyzer`

Benötigt:

```text
change.changed_paths
```

Produziert:

```text
api.openapi.files_changed
```

Im MVP nur Pfad- und Dateierkennung, kein semantischer OpenAPI-Diff.

#### `DatabaseMigrationFileAnalyzer`

Benötigt:

```text
change.changed_paths
```

Produziert:

```text
database.migration.files_changed
```

Erkennt typische Flyway- und Liquibase-Pfade.

#### `CommitRequestAnalyzer`

Erhält Kontext vom Host Adapter und produziert:

```text
commit.requested
commit.message
```

---

## 13. Plugin-Modell

Ein Plugin ist ein installierbares Python-Paket, das Analyzer oder Policy Packs registriert.

```python
from typing import Protocol


class EngineeringPolicyPlugin(Protocol):
    def descriptor(self) -> "PluginDescriptor":
        ...

    def analyzers(self) -> tuple[Analyzer, ...]:
        ...

    def policy_packs(self) -> tuple["PolicyPackProvider", ...]:
        ...
```

### Discovery über Python Entry Points

```toml
[project.entry-points."engineering_policy.plugins"]
git = "engineering_policy_git.plugin:GitPlugin"
java = "engineering_policy_java.plugin:JavaPlugin"
openapi = "engineering_policy_openapi.plugin:OpenApiPlugin"
```

Laden:

```python
from importlib.metadata import entry_points

plugin_entries = entry_points(group="engineering_policy.plugins")
plugins = [entry.load()() for entry in plugin_entries]
```

### Begriffsabgrenzung

- Nutzer installieren Plugins.
- Plugins registrieren Analyzer.
- Die Engine plant Analyzer.
- Analyzer produzieren Facts.
- Der Resolver wählt Policies.

---

## 14. Analyzer-Auswahl

### Ziel

Nur Analyzer ausführen, deren Facts für potenziell relevante Policies benötigt werden.

### MVP-Verfahren

1. Policies anhand des kanonischen Events vorfiltern.
2. Benötigte Facts aus den `when`-Bedingungen sammeln.
3. Basis-Analyzer ausführen:
   - Repository Technology
   - Git Change
4. Fehlende Facts über die Analyzer Registry auflösen.
5. Analyzer-Abhängigkeiten rekursiv ergänzen.
6. Nicht unterstützte Analyzer überspringen.
7. Fehlende Provider als `unavailable` markieren.
8. Analyzer topologisch sortieren und ausführen.
9. Facts im `FactStore` speichern.
10. Policies final auflösen.

### Auswahl bei mehreren Providern

Priorität:

1. explizit konfigurierter Provider
2. Unterstützung des Repository-Kontexts
3. erwartete Präzision
4. niedrigere Kosten
5. stabile ID als Tie-Breaker

Im MVP sollte für jeden Fact möglichst nur ein Provider existieren.

---

## 15. Policy Resolution

### Python-Schnittstelle

```python
class PolicyResolver(Protocol):
    def resolve(
        self,
        event: "PolicyEvent",
        candidate_policies: tuple["Policy", ...],
        facts: "FactStore",
    ) -> "PolicyResolution":
        ...
```

### Resolver-Algorithmus

```text
für jede Kandidaten-Policy:
    wenn Event nicht passt:
        überspringen

    wenn keine when-Bedingungen:
        Policy gilt

    sonst:
        alle benötigten Facts laden

        wenn mindestens ein Fact unavailable/missing:
            Policy unresolved

        wenn alle Bedingungen erfüllt:
            Policy applicable

        sonst:
            Policy nicht applicable
```

### Explainability

```json
{
  "policyId": "company.comprehensive-review",
  "reasons": [
    {
      "fact": "change.substantial",
      "actual": true,
      "operator": "equals",
      "expected": true,
      "evidence": [
        "14 production files changed",
        "827 total lines changed"
      ]
    }
  ]
}
```

---

## 16. MCP-Tools des MVP

Der Server verwendet das offizielle Python MCP SDK und läuft lokal über `stdio`.

Bei `stdio` dürfen normale Logs niemals auf `stdout` geschrieben werden. Logs gehen auf `stderr` oder in Dateien.

### 16.1 `resolve_policies`

Input:

```json
{
  "event": "before_completion",
  "baseRevision": "main",
  "targetRevision": "WORKTREE",
  "taskId": "optional-id"
}
```

Output:

```json
{
  "event": "before_completion",
  "applicablePolicies": [
    {
      "id": "company.comprehensive-review",
      "severity": "mandatory",
      "instruction": "Perform a comprehensive review...",
      "reasons": [
        "14 production files changed",
        "827 lines changed"
      ]
    }
  ],
  "unresolvedPolicies": [],
  "warnings": [],
  "analysis": {
    "analyzersExecuted": [
      "git-change",
      "change-size"
    ]
  }
}
```

### 16.2 `explain_policy`

Liefert:

- Beschreibung
- Instruction
- Parameter
- Referenzen
- Herkunft
- Bedingungen
- Beispiele

### 16.3 `inspect_facts`

Diagnose-Tool für Entwicklung und Evaluation.

Es zeigt:

- produzierte Facts
- Quelle
- Confidence
- Evidenz
- ausgeführte Analyzer
- fehlende Provider

### Bewusst nicht enthalten

- `verify_change`
- `run_tests`
- `create_commit`
- `modify_policy`
- `record_policy_applied`

---

## 17. Host-Integration

### Bootstrap-Instruktion

`CLAUDE.md` beziehungsweise `AGENTS.md` enthält nur einen kleinen Vertrag:

```markdown
## Engineering policies

Use the Engineering Policy MCP server:

1. At task start, resolve policies for `task_start`.
2. Before creating a commit, resolve policies for `before_commit`.
3. Before completing a production-code task, resolve policies for
   `before_completion`.
4. Follow all mandatory policies.
5. Do not claim completion while mandatory policy actions remain open.
6. When policy applicability is unresolved, report the uncertainty.
```

### Host Adapter

Aufgaben:

- Host-Lifecycle erkennen
- in kanonisches Event übersetzen
- Repository und Task-Kontext bestimmen
- MCP- oder CLI-Aufruf auslösen
- Ergebnis dem Agenten zurückgeben

### Fallback

Im ersten vertikalen Slice genügt die Bootstrap-Instruktion. Hostspezifische Automatisierung darf den Kern-MVP nicht blockieren.

---

## 18. Telemetrie

### Ziel

Messbarkeit von Anfang an ermöglichen, ohne Dashboard- oder Monitoring-Scope.

### Speicherung

```text
.engineering-policy/telemetry/events.jsonl
```

### MVP-Events

- `policy_resolution_started`
- `analyzer_executed`
- `fact_produced`
- `policy_resolved`
- `policy_resolution_completed`

Beispiel:

```json
{
  "eventType": "analyzer_executed",
  "taskId": "task-123",
  "analyzerId": "git-change",
  "durationMs": 42,
  "factsProduced": 7,
  "warnings": 0,
  "success": true
}
```

### Nicht erfasst

- vollständige Prompts
- Sourcecode-Inhalte
- Diffs
- personenbezogene Profile
- Token-Kosten
- unbelegte Aussage, ob der Agent eine Policy tatsächlich befolgt hat

### Erste Kennzahlen

- Auflösungen pro Policy
- Anteil `applicable`, `not_applicable`, `unresolved`
- Analyzer-Laufzeit
- Facts pro Analyzer
- Policies, die nie ausgelöst werden
- fehlende Fact Provider

---

## 19. Konfiguration

```yaml
schema_version: 1

product:
  id: billing-platform

policy_sets:
  - company/baseline
  - teams/java-backend
  - products/billing

analysis:
  base_revision: main

  production_paths:
    - "src/main/**"

  test_paths:
    - "src/test/**"

  substantial_change:
    production_files: 10
    changed_lines: 500

  openapi_paths:
    - "**/openapi/**"
    - "**/*openapi*.yaml"

  migration_paths:
    - "src/main/resources/db/migration/**"
    - "**/changelog/**"

telemetry:
  enabled: true
  path: ".engineering-policy/telemetry/events.jsonl"
```

---

## 20. Python-Projektstruktur

```text
engineering-policy-mcp/
├── pyproject.toml
├── uv.lock
├── README.md
├── docs/
│   ├── architecture.md
│   ├── policy-format.md
│   └── host-integration.md
├── src/
│   └── engineering_policy/
│       ├── domain/
│       ├── catalog/
│       ├── facts/
│       ├── analyzers/
│       ├── plugins/
│       ├── resolver/
│       ├── telemetry/
│       ├── mcp/
│       ├── cli/
│       └── java_support/
├── plugins/
│   ├── engineering-policy-plugin-git/
│   ├── engineering-policy-plugin-java/
│   └── engineering-policy-plugin-openapi/
└── tests/
    ├── unit/
    ├── integration/
    ├── fixtures/
    └── host_smoke/
```

Für den MVP kann zunächst ein einzelnes Python-Paket verwendet werden. Plugin-Grenzen werden dennoch durch Python-Protokolle und Entry Points vorbereitet.

Die Plattform enthält keinen Java-Anwendungscode. Java-/Kotlin-Projekte werden über Dateisystem, Git, Maven, Gradle und optionale JVM-Werkzeuge analysiert.

---

## 21. Technologieentscheidungen

### Python

**Python 3.12 oder neuer**

Gründe:

- offizielles Tier-1-MCP-SDK
- schnelle Entwicklung
- einfache lokale Distribution über `uvx`
- gutes Ökosystem für CLI, YAML, JSON Schema und Telemetrie
- geeignet für Plugin- und Analyzer-Architekturen

### Projekt- und Paketverwaltung

**uv**

Entwicklung:

```bash
uv sync
uv run pytest
uv run engineering-policy serve
```

Endanwender:

```bash
uvx engineering-policy-mcp serve
```

### MCP SDK

**Offizielles Python MCP SDK**

Die MCP-Schicht bleibt hinter einem kleinen Adapter.

### Datenmodelle

- Pydantic oder immutable Dataclasses
- PyYAML oder `ruamel.yaml`
- `jsonschema` für Schema-Validierung

### CLI

- Typer

Kommandos:

```bash
engineering-policy validate
engineering-policy doctor
engineering-policy facts
engineering-policy resolve
engineering-policy serve
```

### Logging

- Python `logging`
- bei `stdio` nur `stderr`
- optional `RotatingFileHandler`

### Tests

- pytest
- pytest-cov
- temporäre Git-Repositories über `tmp_path`
- Fixture-Repositories für Java, Kotlin, Maven und Gradle

### Java-/Kotlin-Analyse

Im MVP:

- Dateisystem
- Git
- Build-Dateien
- Pfadmuster

Später optional:

- Maven Wrapper
- Gradle Wrapper
- OpenAPI-Diff
- Revapi
- japicmp
- ArchUnit-Ergebnisse
- JUnit XML
- JaCoCo

---

## 22. CLI-Anforderungen

### `validate`

Validiert:

- Repository-Konfiguration
- Policy-Schema
- eindeutige Policy-IDs
- bekannte Events
- bekannte Fact Keys
- verfügbare Analyzer

### `doctor`

Prüft:

- Python-Version
- Git-Verfügbarkeit
- Git-Repository
- MCP-Konfiguration
- Policy-Sets
- Plugins
- Telemetrie-Verzeichnis
- optional Java, Maven und Gradle

### `facts`

```bash
engineering-policy facts \
  --base main \
  --target WORKTREE
```

### `resolve`

```bash
engineering-policy resolve \
  --event before_completion \
  --base main \
  --target WORKTREE
```

### `serve`

Startet den `stdio`-MCP-Server.

CLI und MCP verwenden dieselbe Application-Logik.

---

## 23. Sicherheitsmodell

### MVP

- nur lokaler Repository-Zugriff
- read-only Git-Kommandos
- keine Netzwerkzugriffe
- keine Secrets lesen
- keine Shell-Kommandos aus Policy-YAML ausführen
- keine Plugin-Downloads zur Laufzeit
- Plugins nur aus installierten Python-Paketen
- Pfade auf Repository-Root begrenzen

### Sichere Prozessausführung

```python
subprocess.run(
    [
        "git",
        "-C",
        str(repository_root),
        "diff",
        "--numstat",
        base_revision,
    ],
    check=True,
    capture_output=True,
    text=True,
    timeout=30,
)
```

Keine Shell-Konkatenation und kein `shell=True`.

---

## 24. Beispielablauf

### Aufgabe

> Implementiere einen neuen öffentlichen Endpoint im Billing-Service.

### `task_start`

Der Agent ruft `resolve_policies` auf und erhält allgemeine sowie produktbezogene Start-Policies.

### Implementierung

Der Agent entwickelt Java-Code, OpenAPI-Datei und Tests.

### `before_completion`

Analyzer produzieren:

```text
repository.language.java = true
repository.build_system = gradle
change.production_files.count = 7
change.lines.total = 438
api.openapi.files_changed = true
database.migration.files_changed = true
change.substantial = false
```

Der Resolver wählt:

- API-Kompatibilität prüfen
- Datenbankmigration berücksichtigen
- Integrationstests durchführen
- gegebenenfalls produktspezifischen Review

### `before_commit`

Die Engine liefert die Conventional-Commit-Policy.

Der Agent verwendet:

```text
feat(invoice): add cancellation endpoint
```

---

## 25. Teststrategie

### Unit Tests

- Policy-Parsing
- Operatoren
- Resolver
- Analyzer-Planung
- FactStore
- Telemetrie

### Analyzer Contract Tests

```text
fixture: java-gradle-openapi-change
expected:
  repository.language.java = true
  repository.build_system = gradle
  api.openapi.files_changed = true
```

### Policy Resolution Fixtures

```yaml
event: before_completion

facts:
  change.substantial: true

expected:
  applicable:
    - company.comprehensive-review
```

### Integrationstests

1. temporäres Git-Repository erzeugen
2. Java-/Gradle-Dateien hinzufügen
3. Baseline committen
4. Dateien ändern
5. Analyzer ausführen
6. Policies auflösen
7. MCP-Antwort prüfen

### Host-Smoketests

Mit Claude Code und Codex:

- wird das Tool aufgerufen?
- wird `mandatory` berücksichtigt?
- wie beeinflusst die Toolbeschreibung das Verhalten?
- welche Antwortgrösse funktioniert?
- welche Policy-Informationen werden ignoriert?

---

## 26. Evaluation des Agentenverhaltens

### Szenario A: Conventional Commit

Vergleich:

1. nur Bootstrap-Instruktion
2. Bootstrap + MCP Policy
3. Bootstrap + MCP Policy + Git-Hook

### Szenario B: umfassender Review

Fixture mit grossem Java-Diff.

Prüfung:

- MCP wird aufgerufen
- Review wird durchgeführt
- definierte Reviewbereiche werden abgedeckt
- Findings werden vor Abschluss behoben

### Szenario C: OpenAPI-Änderung

Fixture mit geänderter OpenAPI-Datei.

Prüfung:

- API-Policy wird ausgewählt
- Agent erwähnt Kompatibilität
- Agent erkennt oder vermeidet Breaking Changes

Die Ergebnisse werden zunächst manuell in Markdown dokumentiert.

---

## 27. Umsetzungsplan

### Woche 1: Fundament

- Python-Projekt mit uv
- Domänenmodell
- YAML Policy Loader
- JSON-Schema-Validierung
- CLI `validate`
- erste drei Policies

### Woche 2: Facts und Analyzer

- FactStore
- Plugin API
- Python Entry Points
- Repository Technology Analyzer
- Git Change Analyzer
- Change Size Analyzer
- CLI `facts`

### Woche 3: Resolver und Telemetrie

- Analyzer Registry
- einfacher Planner
- Policy Resolver
- Explainability
- JSONL-Telemetrie
- CLI `resolve`

### Woche 4: MCP und Hosts

- `stdio` MCP Server
- `resolve_policies`
- `explain_policy`
- `inspect_facts`
- Claude-Code-Konfiguration
- Codex-Konfiguration
- Bootstrap-Dateien

### Woche 5: Dogfooding

- Einsatz in mindestens einem echten Java-Projekt
- Evaluation der drei Szenarien
- Toolbeschreibungen optimieren
- Packaging über PyPI/uvx
- Dokumentation
- erstes internes oder öffentliches Release

---

## 28. MVP-Akzeptanzkriterien

Der MVP ist abgeschlossen, wenn:

1. Die Python-Plattform lokal in einem Java- oder Kotlin-Projekt gestartet werden kann.
2. Claude Code und Codex denselben MCP-Server verwenden können.
3. Company-, Team- und Produkt-Policy-Sets geladen werden.
4. Mindestens fünf Facts automatisch erzeugt werden.
5. Mindestens drei Analyzer als Plugin-Beiträge registriert sind.
6. `resolve_policies` für alle drei kanonischen Events funktioniert.
7. Conventional-Commit- und Review-Policies in einem echten Workflow genutzt werden.
8. Jede Policy-Auflösung Explainability enthält.
9. Analyzer- und Policy-Entscheidungen als JSONL-Telemetrie vorliegen.
10. CLI und MCP dieselbe Application-Logik verwenden.
11. Mindestens ein reales Java-Projekt als Dogfooding-Repository dient.
12. Die wichtigsten Grenzen dokumentiert sind.

---

## 29. Verschobene Erweiterungen

- semantischer OpenAPI-Diff
- Java Binary API Analyzer
- Maven- und Gradle-Modulgraph
- Kotlin-Compiler-/LSP-Integration
- .NET-Plugin
- Verifier API
- zentrale Policy-Repositories
- HTTP-MCP
- signierte Policy Packs
- CI-Adapter
- OpenTelemetry-Export
- Dashboard
- Policy-Ausnahmen
- Service Catalog oder CODEOWNERS als Context Sources

---

## 30. Hauptrisiken

### Agent ruft MCP nicht auf

Massnahmen:

- kleine Bootstrap-Instruktion
- klare Toolbeschreibung
- Host-Adapter
- Evaluation mit beiden Hosts
- CI bleibt finale Absicherung

### Policy-YAML wächst zur Programmiersprache

Massnahmen:

- nur flache Bedingungen
- wenige Operatoren
- keine Skripte
- Schema nur aufgrund echter Use Cases erweitern

### Analyzer-Scope wächst

Massnahmen:

- MVP nur Git-, Pfad- und Repository-Facts
- keine AST- oder LSP-Analyse
- neue Analyzer nur für echte Policies

### Messbarkeit bläht den Scope auf

Massnahmen:

- nur JSONL
- fünf Domain Events
- kein Backend
- kein Dashboard
- keine personenbezogene Auswertung

### Python-Plattform analysiert JVM-Projekte

Massnahmen:

- JVM-spezifische Logik konsequent in Plugins kapseln
- Maven-/Gradle-Wrapper des Zielprojekts nutzen
- externe Werkzeuge als optionale Abhängigkeiten behandeln
- fehlende Werkzeuge als `unavailable`, nicht als `false`, modellieren

---

## 31. Architekturentscheidungen

### ADR-001: Python als Plattform-Sprache

Die Plattform wird in Python umgesetzt. Ausschlaggebend sind das offizielle Tier-1-MCP-SDK, schnelle Entwicklung und einfache Distribution über `uvx`.

Die analysierten Zielprojekte sind primär Java und optional Kotlin.

### ADR-002: Offizielles Python MCP SDK

Die MCP-Integration verwendet das offizielle Python SDK. Die SDK-Nutzung bleibt hinter einem Adapter.

### ADR-003: Lokaler `stdio`-Server

Der MVP läuft als lokaler Unterprozess. Es ist keine Repository-Authentisierung nötig; Quellcode bleibt lokal.

### ADR-004: Analyzer als Plugin-Beiträge

Analyzer sind read-only Fact Producer. Plugins sind installierbare Python-Pakete, die Analyzer und Policy Packs beitragen.

### ADR-005: Keine LLM-Aufrufe im Server

Die Plattform löst Policies deterministisch auf. Claude Code oder Codex interpretiert und befolgt die Instructions.

### ADR-006: Telemetrie als JSONL

Messbarkeit wird von Beginn an unterstützt, ohne eine Observability-Plattform zu bauen.

### ADR-007: Keine Verifier im MVP

Zunächst wird untersucht, wie Coding Agents Policy-Instruktionen aufnehmen und anwenden.

---

## 32. Offene Fragen

1. Wie wird `WORKTREE` exakt modelliert?
2. Wie werden staged und unstaged Änderungen unterschieden?
3. Welche Antwortgrösse ist für Claude Code und Codex optimal?
4. Wird `task_start` im MVP automatisiert oder nur instruiert?
5. Wie wird eine Task-ID hostübergreifend erzeugt?
6. Welche Policy-Details gehören direkt in `resolve_policies`?
7. Welche Java-spezifischen Facts sind nach dem MVP am wertvollsten?
8. Wann lohnt sich ein Maven-/Gradle-Analyzer gegenüber Pfadheuristiken?
9. Welche Telemetriedaten sind im Unternehmenskontext zulässig?
10. Welches reale Java-Projekt dient als erstes Dogfooding-Repository?

---

## 33. Unmittelbar nächster Schritt

Zuerst wird ein kleiner vertikaler Slice implementiert:

```text
Policy YAML laden
        ↓
Git Change Facts erzeugen
        ↓
Review Policy auflösen
        ↓
CLI-Ausgabe
        ↓
Telemetrie-Event schreiben
```

Die erste End-to-End-Demo:

> In einem Java-Git-Repository wird ein ausreichend grosser Diff erzeugt.  
> `engineering-policy resolve --event before_completion` liefert die verpflichtende Comprehensive-Review-Policy mit nachvollziehbarem Grund und schreibt strukturierte Telemetrie.

Erst danach wird der MCP-Adapter ergänzt.

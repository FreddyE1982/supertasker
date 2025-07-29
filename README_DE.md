# Kalender App

Dieses Projekt bietet eine einfache Kalenderanwendung mit einer REST -API und einer strombeleuchteten GUI. Benutzer können Termine erstellen, aktualisieren, löschen und auflisten.
Es unterstützt auch die Verwaltung von Aufgaben mit optionalen Unteraufgaben. Unteraufgaben sind nützlich, um große Aufgaben in kleinere Schritte zu unterteilen, was für Benutzer mit ADHS hilfreich sein kann.
Darüber hinaus unterstützen die Aufgaben nun ** Fokussitzungen **, um kurze, zeitgesteuerte Arbeitsintervalle zu fördern. Diese Funktion wurde mit ADHS -Benutzern entwickelt, um die Konzentration zu unterstützen.
Aufgaben haben auch eine ** Priorität ** von 1 bis 5, um ADHS-Benutzern zu helfen, zu ermitteln, worauf sie sich konzentrieren sollen.

## Anforderungen

- Python 3.10+
- Pip

Abhängigkeiten installieren:

`` `bash
PIP Installation Fastapi Uvicorn
`` `

## Ausführen der API

`` `bash
Uvicorn App.Main: App
`` `

Die API wird unter `http: // localhost: 8000` erhältlich sein.
Die API enthält ein OpenAPI -Schema bei `http: // localhost: 8000/openAPI.json` und interaktive Dokumente unter` http: // localhost: 8000/docs`.

### Protokollierung

Setzen Sie die Protokollebene mit `log_level` in` config.yaml` oder als Umgebungsvariable.

## Ausführen der Stromflächen -GUI

`` `bash
streamlit run streamlit_app.py
`` `

### Dunkelemodus

Die GUI unterstützt ein optionales dunkles Thema. Aktivieren Sie es über den ** dunklen Modus **
Kontrollkästchen oben in der Anwendung.

## Ausführen von Tests

Alle Tests durchführen:

`` `bash
Pytest
`` `

Nur die GUI -Tests durchzuführen:

`` `bash
PyTest -Tests/test_gui.py
`` `
Führen Sie Tests mit Abdeckung aus:
`` `bash
Berichterstattung laufen -m PyTest
Berichterstattung HTML
`` `
Berichte über Berichte erscheinen in "htmlcov".

Dieses Projekt verwendet Pre-Commit-Hooks zum Auslegen, Formatieren und Typ-Überprüfungen. Installieren Sie sie mit:
`` `bash
Vor-Commit-Installation
`` `
Die Hooks erzwingen schwarze Formatierung, ISORT -Import -Bestellung, Flake8 -Stilprüfungen und MyPy -Typanalyse.


## automatische Abhängigkeitsinstallation

Importieren des "autoInstaller" -Moduls installiert fehlende Python -Pakete
im Projekt entdeckt. Setzen Sie `autoInstall_path`, um ein anderes Verzeichnis zu scannen
Vor dem Import des Moduls.

## Subtask -API

Unteraufgaben werden über die folgenden Endpunkte verwaltet:

- `post/tasks/{task_id}/subtasks` - Erstellen Sie eine neue Subtask für eine Aufgabe
- `get/tasks/{task_id}/subtasks` - Listen Sie Unteraufgaben einer Aufgabe auf
- `put/tasks/{task_id}/subtasks/{subtask_id}` - Aktualisieren Sie eine Untertask
- `delete/tasks/{task_id}/subtasks/{subtask_id}` - eine Subtask löschen

## Aufgabe Priorität

Jede Aufgabe hat eine Priorität von 1 (niedrigster) bis 5 (höchster). Verwenden Sie dieses Feld, wenn
Erstellen oder Aktualisieren von Aufgaben, um wichtige Elemente hervorzuheben.

## Kategorien

Termine und Aufgaben können optional zu Kategorien gehören. Kategorien erstellen über
`Post /category` und verweisen Sie mit` category_id` beim Erstellen oder
Planungsaufgaben oder Termine. Die Planer -Gruppenaufgaben derselben Kategorie
Nahe zusammen, wenn `` category_context_window`` genügend Raum bietet.
Kategorien können auch `` bevorzugt_start_hour`` und `` bevorzugt_end_hour`` definieren
Diese Aufgaben dieser Kategorie sind also in einem bestimmten Zeitfenster geplant.
Zusätzlich kann `` Energy_curve`` 24 comma -getrennte Zahlen angeben
Relative Energieniveaus für jede Stunde. Beim Set multipliziert der Planer die
Allgemeine Energiekurve mit dieser Kategoriekurve für die intelligentere Zeitauswahl.

## FOCUS Session API

Fokussitzungen helfen dabei, die Arbeit in überschaubare Stücke zu unterteilen. Endpunkte:

- `post/tasks/{task_id}/focus_Sessions`` - Starten Sie eine Fokussitzung
- `get/tasks/{task_id}/Focus_Sessions` - - List Focus -Sitzungen für eine Aufgabe
- `put/tasks/{task_id}/Focus_Sessions/{session_id}` - Aktualisieren Sie eine Fokussitzung
- `delete/tasks/{task_id}/focus_sessions/{session_id}` - eine Fokussitzung löschen

## Automatische Aufgabenplanung

Erstellen und planen Sie Aufgaben in einem Schritt mit `post /tasks /plan`.
Senden Sie JSON mit "title", `cressess`,` geschätzt_difficulty`,,
`Estatatated_duration_Minutes`,` fata_date` und optional `priority`,,
`category_id` oder` category_day_weight` zu gruppenbezogenen Arbeiten und bevorzugen Tage
Das enthält bereits Aufgaben derselben Kategorie.
Der Service teilt die Arbeit in 25-minütige Fokus-Sitzungen mit
Pomodoro-Stil bricht und sorgt für keine Überschneidung mit vorhandenen Kalendereinträgen.
Die Sitzungen sind mit allen aktuellen Terminen und Aufgaben zusammengefasst, damit die Arbeit funktioniert
Passt natürlich in die freien Slots des Tages. Jede Fokussitzung schafft auch
Eine entsprechende Subtask, so dass große Aufgaben automatisch in überschaubar sind
Teile.
Der Planer ehrt die Umgebung von `` Work_start_hour`` und `` work_end_hour``
Variablen sowie `` max_Sessions_per_day`` sich an die benutzerdefinierten Arbeitszeiten anpassen
und Arbeitsbelastungsverteilung. Wenn `` intelligent_day_order`` es aktiviert ist
Wiege die verfügbare Energie auch jeden Tag mit `` Energy_day_order_weight``
so dass Sitzungen an Tagen mit genügend Zeit und hoher Energie landen. Zusätzlich
Einstellungen ermöglichen eine erweiterte Abstimmung:

- `` Session_length_Minutes`` - Dauer jeder Fokussitzung (Standard 25)
- `` intelligent_session_Length`` - skalierende Sitzungslänge basierend auf Schwierigkeiten und Priorität, wenn auf `` 1`` oder `true`` (Standard deaktiviert) eingestellt ist
- `` min_session_length_minutes`` - - minimal zulässige Sitzungslänge Wenn intelligente Skalierung aktiviert ist (Standard `` Session_LENGH_MINUTES``)
- `` max_session_length_minutes`` - maximal zulässige Sitzungslänge Wenn intelligente Skalierung aktiviert ist (Standard `` Session_length_Minutes``)
- `` Short_break_Minutes`` - Kurzpausenlänge (Standard 5)
- `` long_break_minutes`` - Long Break Länge (Standard 15)
- `` intelligent_breaks`` - Skalierungslänge basierend auf Aufgabenschwierigkeiten, wenn auf `` 1`` oder `` true`` (Standard deaktiviert) festgelegt wurde
- `` min_short_break_minutes`` - - Mindestkurzpause Wenn intelligente Pausen aktiviert sind (Standard `` Short_break_Minutes```)
- `` max_short_break_minutes`` - Maximal Short Break Wenn intelligente Pausen aktiviert sind (Standard `` Short_break_minutes``)
- `` min_long_break_minutes`` - - minimale lange Pause Wenn intelligente Pausen aktiviert sind (Standard `` long_break_minutes```)
- `` max_long_break_minutes`` - - Maximal Long Break Wenn intelligente Pausen aktiviert sind (Standard `` long_break_minutes``))
- `` Sessions_before_long_break`` - Anzahl der Sitzungen vor einer langen Pause
  wird eingefügt (Standard 4)
- `` max_Sessions_per_day`` - Maximale Sitzungen pro Aufgabe pro Tag (Standard 4)
- `` Daily_Session_Limit`` - Maximale Sitzungen von allen Aufgaben an einem einzigen Tag
  (Standard unbegrenzt)
- `` intelligent_day_order`` - bevorzugen Tage mit mehr Freizeit bei der Planung
  Fokussitzungen (Standard deaktiviert)
- `` Energy_day_order_weight`` - zusätzliches Gewicht für Tage mit höher verfügbaren verfügbaren
  Energie Wenn die intelligente Tagesordnung aktiviert ist (Standard 0)
- `` woekday_energy``- Komma-getrennte Liste von sieben Zahlen, die Verwandte geben
  Energie für jeden Wochentag ab Montag. Verwendet mit intelligenter Tagesordnung bis
  Bevorzugen Sie Tage, die im Allgemeinen einen besseren Fokus bieten (standardmäßig alle `1``)
- `` Work_days``- von Comma getrennte Liste der Wochentagsnummern (0 = Montag), die sind
  als Arbeitstage angesehen. Standardmäßig sind alle Tage erlaubt.
- `` lunch_start_hour`` - Stunde, wenn eine tägliche Mittagspause beginnt (Standard 12)
- `` lunch_duration_minutes`` - Länge der Mittagspause (Standard 60)
- `` Schwierigkeitswürdig_Weight`` - Schwierigkeitsgewicht bei der Berechnung der Bedeutung (Standard 1)
- `` priority_weight`` - Prioritätsgewicht bei der Berechnung der Bedeutung (Standard 1)
- `` dringcy_weight`` - Gewicht des Fälligkeitsdatums Dringlichkeit bei der Berechnung der Bedeutung (Standard 1)

- `` low_energy_start_hour`` - Start der niedrigen Energiezeit, um schwierige Aufgaben zu vermeiden (Standard 14)
- `` low_energy_end_hour`` - Endstunde der niedrigen Energiezeit (Standard 16)
- `` High_energy_start_hour`` - bevorzugte Startstunde für wichtige Aufgaben (Standard 9)
- `` High_energy_end_hour`` - Ende des bevorzugten Hochenergiefensters (Standard 12)
- `` fatigue_break_factor`` - - Multiplizieren Sie die Bruchlänge mit `` 1 + sissions_today * faktor
- `` Energy_curve```- Komma-getrennte 24 Zahlen, die Energieniveaus pro Stunde darstellen, um bessere Startzeiten zu wählen (optional)
- `` intelligent_slot_selection`` - - Wählen Sie die beste Freizeit an einem Tag basierend auf dem
  höchster Energieniveau (Standard deaktiviert)
- `` SLOT_STEP_MINUTES`` - Minuten zwischen den Startzeiten der Kandidaten, wenn intelligent
  Die Slot -Auswahl ist aktiviert (Standard 15)
- `` Deep_work_threshold``- Schwierigkeitsgrad von 1-5, die die Planung auslöst
  Alle Fokussitzungen für diese Aufgabe nacheinander im größten verfügbaren Block
  (Standard 0 deaktiviert Tiefe Arbeitsplanung)
- `` Daily_difficulty_limit`` - maximale Gesamtschwierigkeit, die pro Tag geplant ist
  Alle Aufgaben (Standard 0 deaktiviert Schwierigkeitsgrad)
- `` Daily_energy_limit`` - Maximale Summe von `` Schwierigkeitsgrad * Sitzungslänge``
  pro Tag über alle Aufgaben geplant (Standard 0 deaktiviert den Energieausgleich)
- `` transition_buffer_minutes``- Minuten der Vorbereitung und Abschlusszeit vor und nach jeder Fokussitzung (Standard-0)
- `` Intelligenz_Transition_Buffer`` - Skalierpuffer Minuten mit Schwierigkeiten bei Aufgaben, wenn auf `` 1`` oder `true`` (Standard deaktiviert) eingestellt wurde
- `` category_context_window``- Minuten um vorhandene gleichen Kategorienaufgaben, die sie bei der Planung bevorzugen sollen (Standard 60)
- `` category_day_weight`` - Zusätzliche Gewicht bevorzugen Tage, die bereits Ereignisse derselben Kategorie enthalten (Standard 0)
- `` productivity_history_weight`` - Gewicht der Vervollständigungsraten der vergangenen Sitzung pro Stunde bei Slots (Standard 0)
- `` productivity_half_life_days`` - Tage, bis historische Gewichte bei der Berechnung der Produktivität halbieren (Standard 30)
- `` category_productivity_weight``- Gewicht der kategoriespezifischen Abschlussraten bei Auswahl von Slots (Standard 0)
- `` Spaced_Repetition_factor`` - - Multiplizieren Sie die Lücke zwischen aufeinanderfolgenden Sitzungen mit diesem Faktor für die Wiederholung von Abstand (Standard 1 deaktiviert den Abstand)
- `` session_count_weight`` - Strafe pro bereits geplanter Sitzung an einem Tag bei der Auswahl der Planungstage (Standard 0)
- `` Schwierigkeitswürdig_Load_weight`` - Strafe basierend auf der bereits an einem Tag geplanten Gesamtschwierigkeit (Standard 0)
- `` Energy_Load_weight`` - Strafe basierend auf der bereits an einem Tag geplanten Gesamtergielast (Standard 0)
- `` Preferred_Start_Hour`` und `` Vorzug_end_Hour`` - Optionale Felder in Kategorien, die die Planung dieses Fensters einschränken
- `` Energy_curve`` - optionale 24 Comma -Werte für die Gewichtung der Kategorien für
  Kategorieaufgaben

Schwierigere oder hohe Prioritätsaufgaben werden früher am Tag platziert
Leichter sind später geplant und verbreiten Sitzungen über Tage hinweg, wenn dies erforderlich ist
schlauer und personalisiertere Planung. Wichtige Aufgaben beginnen früher in der
Zeitplan durch Gewichtungsschwierigkeit, Priorität und Dringlichkeit mit dem Gewicht
Variablen oben. Die Sitzungszeiten berücksichtigen auch Dringlichkeit basierend darauf, wie schnell eine Aufgabe ist
fällig und der Planer gleicht die Anzahl der Fokussitzungen pro Tag in Einklang, damit die Arbeit funktioniert
ist bis zur Frist gleichmäßig verteilt.
Die Einstellungen für die Mittagspause stellen sicher, dass die Planung zwischen `` lunch_start_hour`` pikt
und `` lunch_start_hour`` plus `` lunch_duration_minutes`` Also fokussierte Sitzungen nie
Überlappung mit dieser täglichen Pause.
Harte Aufgaben werden auch aus dem Fenster "` `low_energy_start_hour`` zu` `low_energy_end_hour`` veröffentlicht, um die Sitzungen produktiv zu halten.
Wichtige Aufgaben werden zusätzlich in das Fenster "High_energy_Start_Hour" "zu` High_energy_end_hour`` "gegebenenfalls nach Möglichkeit gezogen, sodass die anspruchsvollste Arbeit während der Spitzenfokuszeiten auftritt.
Durch die Bereitstellung eines `` Energy_curve`` können der Planer -Kartierungsaufgabe für diese Energieniveaus so wichtig ist, dass sehr wichtige Aufgaben zu Zeiten mit höheren Energiewerten beginnen, während weniger kritische in niedrigere Energieperioden eingesetzt werden.
Aktivieren von `` Intelligent_Slot_Selection`` Verfeinert die Platzierung durch Scannen weiter
Alle freien Slots an einem Tag und die Zeit mit dem höchsten Energiewert aussuchen
Die Arbeit kommt immer auf, wenn der Fokus voraussichtlich am stärksten ist.

## Befehlszeilenschnittstelle
Verwenden Sie "Python cli.py add" und `Python cli.py list", um Aufgaben aus dem Terminal zu verwalten. Konfigurieren Sie die API -URL in `config.yaml` oder über die Umgebungsvariable von` api_url`.

## generierter API -Client

Das Paket `openAPI_Client` wird aus dem OpenAPI-Schema unter Verwendung von` openAPI-Python-client` generiert. Wiederherstellen Sie es mit:

`` `bash
OpenAPI-Python-Client generieren-über
`` `


## Docker Compose
Ein Beispiel "Docker-compose.yml" wird bereitgestellt, um die API in einem Container auszuführen.

## Bereitstellung

Anweisungen zum Erstellen des Docker -Images finden Sie unter [Deployment.md] (Deployment.md)
und Ausführen des vollständigen Stacks mit Postgresql.


Siehe [user_guide.md] (user_guide.md) für Nutzungsanweisungen und [FAQ.MD] (FAQ.MD) zur Fehlerbehebung.

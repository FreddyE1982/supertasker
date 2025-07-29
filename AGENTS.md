 UNANTASTBARE GRUNDREGELN
Diese Regeln sind absolut. Sie dürfen niemals verletzt, ignoriert, ersetzt oder abgeschwächt werden. Der Agent darf sie nur ERWEITERN, niemals verändern oder relativieren.

NIEMALS vereinfachen.

Der Agent darf keine Vereinfachungen irgendeiner Art vornehmen.

Kein „Democode“, keine „grobe Implementierung“, keine „Minimalversion“. Alles muss immer vollständig, produktionsreif und maximal exakt umgesetzt werden – exakt so, wie der Benutzer es vorgibt oder impliziert.

Funktionalität darf niemals entfernt werden.

Keine bestehende GUI-Funktionalität darf entfernt werden.

Keine Klasse, Funktion oder Schnittstelle darf gestrichen oder entkernt werden.

Trenne Verantwortlichkeiten strikt.

Eine Klasse = eine Verantwortung.

Keine Funktionen außerhalb von Klassen.

Vererbung ist zu bevorzugen, wo immer dies möglich und logisch ist.

Erweiterung statt Ersetzung.

Bestehende Funktionen müssen modifiziert oder erweitert werden, niemals ersetzt oder neu geschrieben.

Niemals eine „Version 2“ einer Funktion bauen. Immer die bestehende Funktion anpassen.

Mathematische Formeln sind sakrosankt.

Keine Kürzungen, keine Variablenentfernung, keine Vereinfachungen.

Kein Term darf verändert oder entfernt werden – auch nicht „aus Performancegründen“.

Gleichungen und Algorithmen sind unverändert beizubehalten oder zu erweitern.

Persistenz ist Pflicht.

Alle Daten müssen in einer Datenbank gespeichert werden.

Dateiimporte dienen ausschließlich der Datenbankbefüllung. Danach ist der Zugriff nur über die DB erlaubt.

Tests sind Pflicht und vollständig.

Nach jeder Codeänderung: vollständige Testabdeckung.

Tests basieren ausschließlich auf echten Daten und echten REST-Endpunkten – kein Monkeypatching erlaubt.

Tests müssen erwartete Werte exakt prüfen – keine relativen Toleranzen, keine Platzhalter.

Alle Warnungen, die beim Testen auftreten, müssen durch Codekorrektur behoben werden.

Testdaten müssen vollständig sein.

Der Agent erstellt bei Bedarf automatisch sinnvolle, vollständige Testdaten und bestimmt im Voraus die zu erwartenden Resultate, die dann exakt überprüft werden.

Tests müssen REST nutzen.

Da Streamlit nicht direkt getestet werden kann, müssen Tests alle Funktionen über REST-Endpunkte auslösen.

Rollback ist erlaubt – auf Anweisung.

Wenn der Benutzer den letzten Merge-PR zurückgesetzt haben will, ist dies zu tun, auch wenn es andere Regeln bricht.

Testselektion bei GUI-Arbeit.

Wenn der Benutzer ausdrücklich die GUI-Tests beauftragt, dürfen nur GUI-relevante Tests laufen.

Die „alles testen“-Regel ist in diesem Fall temporär außer Kraft.

When testing, any failed tests should be logged into a FAILEDTESTS.md that is persisted.

the agent is NOT to run ANY tests if the agent has not made any changes to code yet.
if the user says "relevant tests only", then the agent is to run tests that are relevant to the changed code pieces ONLY even if that contradicts another rule

🟦 STREAMLIT GUI – Pflicht zur Visualisierung
Jede Funktionalität muss auch in der GUI vollständig zugänglich sein.

GUI-Erstellung ist Pflicht.

Jede neue Funktion muss über eine Streamlit-GUI zugänglich sein.

Die GUI ist in logisch gruppierte Tabs zu strukturieren. Bestehende Tabs sind zu nutzen, neue nur, wenn es logisch notwendig ist.

Doppelte Tabs sind verboten. Beispiel: Es darf nur EIN Statistik-Tab existieren.

GUI muss auf Mobilgeräten korrekt funktionieren.

Die Darstellung muss automatisch erkennen, ob ein Desktop oder Mobilgerät genutzt wird.

Nichts darf weggelassen oder vereinfacht werden. Keine "Lite-Versionen".

Gruppierung mit st.expander.

Funktionalitäten innerhalb eines Tabs sind logisch mit st.expander zu gruppieren.

Nested Expanders sind erlaubt, wenn logisch sinnvoll.

Verwende st.dialog, wo angemessen.

Wie in dieser Dokumentation beschrieben.

Nie bestehende GUI-Funktionen entfernen.

Auch bei Redesigns oder Refactorings muss alles erhalten bleiben, was vorher da war.

GUI-Testpflicht

Die GUI ist vollständig unitzutesten.

Siehe dazu: streamlittestinghowto.md

Es darf kein Tab, kein Element ungetestet bleiben.

Wenn der Agent an den GUI-Tests arbeitet, darf er niemals nur einzelne Elemente testen, sondern muss signifikante Abschnitte bearbeiten (z. B. einen ganzen Tab oder mindestens die Hälfte eines Tabs).

Wenn die GUI verändert wurde, sind die Tests entsprechend zu erweitern.

🟩 DOKUMENTATION – Für Menschen gedacht
README.md ist Pflicht.

Die README.md muss verständlich für Nicht-Experten sein.

Sie ist stets aktuell zu halten.

Sie erklärt Installation, Nutzung, Aufbau, Datenflüsse und Beispiele.

🔧 AGENTENVERHALTEN – Laufzeit
Iteration ist Pflicht.

Der Agent verwendet jede verfügbare Zeit, um Fortschritt zu machen.

Wenn etwas nicht fertig wird, merkt sich der Agent den Zustand und arbeitet beim nächsten Turn sofort weiter.

Regeln dürfen erweitert, aber NIE verändert werden.

Neue sinnvolle Regeln, die sich im Laufe der Entwicklung ergeben, müssen sofort ergänzt werden.

Aber: Keine bestehende Regel darf je überschrieben oder abgeschwächt werden.

🛑 VERBOTENE VERHALTEN
❌ Kein Monkeypatching

❌ Keine Demonstrationen

❌ Keine Teillösungen

❌ Keine Vereinfachung von Algorithmen

❌ Kein Entfernen von GUI-Funktionalität

❌ Kein Verzicht auf Tests

❌ Kein Übergehen von REST bei Tests

❌ Keine mobile GUI-Vereinfachung

❌ Kein „Quickfix“ oder „Workaround“ statt Korrektur

❌ Kein Auslassen von Tabs bei GUI-Tests

## TODO.md ##

Before the agent does ANYTHING it checks if a TODO.md file exists, if yes the agent performs as many steps from that file as it is able during its turn.
Executing steps in TODO.md does always take priority over tasks given by the user UNLESS the user mentions that the given task takes pritority.
If the agent gets a task that it thinks may be to extensive or complex to perform in one agent run, then the agent is to create a TODO.md file and write into it all steps that need to be taken to execute said path.
Whenever the agent finishes a step from the TODO.md, it has to mark that step as "complete" in the TODO.md
If there are no more steps left in the TODO.md, the agent deletes the file. TODO.md MUST be included in commit if present.

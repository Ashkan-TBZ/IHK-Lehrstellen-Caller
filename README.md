# IHK Lehrstellen Caller

IHK Lehrstellen Caller ermöglicht es, mit einem eigenen Suchmuster die Lehrstellenbörse der IHK zu durchsuchen und die Treffer als E-Mail zu verschicken.

## Suchkriterien

Mögliche veränderbare Variablen

```bash
# RECEIVER NAME | Dein Vorname
# EMPFAENGER | Deine E-Mail Adresse
# LOCATION | Postleitzahl
# PERIMETER | Umkreis
# QUERY RAW | Ausbildungsberuf (Abgekürze Variante benutzen! Bsp: Kfm/Kffr für Büromanagement)
# DELAY | Pause bis zum Versand der nächsten E-Mail (in Sekunden! 3600 = 1 Stunde)
# MAX SEARCH | Anzahl der angezeigten Ausbildungsstellen in der E-Mail (1 - 50)
# SORT MODE | Sortierung der Liste (-1 = Normale Sortierung)
# SMTP SERVER | SMTP Serveradresse
# SMTP PORT | SMTP Serverport
# SMTP USER | SMTP Benutzername zum E-Mail Konto (ggf. identisch mit SENDERMAIL)
# SMTP PASS | SMTP Passwort zum E-Mail Konto
# SENDERMAIL | E-Mail Adresse welche als Sender verwendet wird (ggf. identisch mit SMTP USER)
```

## Beispiel E-Mail Ausgabe
![E-Mail preview](https://i.imgur.com/K7wpz8E.png)

## Lizenz
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

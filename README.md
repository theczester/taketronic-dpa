# Taketronic DPA feed

Generuje grafiki produktów z ramką Taketronic i feed XML dla katalogu Meta (zamiennik Cropink, bez limitu produktów).

- Źródło: feed z Apps Script (lista z arkusza „Bestsellers IDs”), sekret `SOURCE_URL`.
- Wynik: `https://theczester.github.io/taketronic-dpa/feed.xml`, odświeżany co godzinę (GitHub Actions).
- Jeśli w źródle jest mniej niż 5 produktów, nowy feed nie jest publikowany (zostaje ostatni dobry).
- Wygląd ramki: `gen.py` (stałe na górze pliku), logo i czcionka w `assets/`.

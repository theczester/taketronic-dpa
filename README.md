# Taketronic DPA feed

Generuje grafiki produktów z ramką Taketronic i feed XML dla katalogu Meta (zamiennik Cropink, bez limitu produktów).

- Źródło: pełny feed Facebook z Selly (sekret `SELLY_FEED_URL`). Ramki dostają wszystkie produkty ze zdjęciem; to, które produkty pokazuje reklama, ustala zestaw produktów w Mecie.
- Wynik: `https://theczester.github.io/taketronic-dpa/feed.xml`, odświeżany co godzinę (GitHub Actions).
- Jeśli w źródle jest mniej niż 5 produktów, nowy feed nie jest publikowany (zostaje ostatni dobry).
- Wygląd ramki: `gen.py` (stałe na górze pliku), logo i czcionka w `assets/`.

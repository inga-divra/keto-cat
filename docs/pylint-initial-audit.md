# Alustava Pylint-tarkastus

Tämä on kehitysvaiheen alustava tarkastus. Lopullinen raportti `pylint-report.md` tehdään sovelluksen lopullisesta versiosta ennen lopullista palautusta.

## 1. Tarkastuksen tarkoitus

Tarkastuksen tavoitteena oli löytää sovelluksen Python-koodista todelliset virheet ja helposti korjattavat laatuongelmat sekä kirjata koodin laadun lähtötaso. Pistemäärää ei yritetty nostaa keinotekoisesti: ilmoitukset korjattiin vain, jos korjaus paransi koodia, ja muut ilmoitukset perusteltiin.

## 2. Ympäristö ja komennot

- Päivämäärä: 5.11.2026
- Python 3.13.7 (koodi on yhteensopiva myös Python 3.12:n kanssa)
- Pylint 4.1.3 (astroid 4.3.4), oletusasetukset, ei omaa asetustiedostoa
- Pylint asennettiin vain kehitysympäristön virtuaaliympäristöön. Se ei ole sovelluksen ajonaikainen riippuvuus.

Tarkastetut tiedostot ovat projektin omat Python-tiedostot. Mukana eivät ole virtuaaliympäristö, yksityinen `config.py`, tietokannat eikä kurssin esimerkkiprojekti.

```
pip install pylint
pylint app.py db.py users.py recipes.py init_db.py seed.py benchmark.py
```

Sama komento ajettiin ennen korjauksia ja niiden jälkeen.

## 3. Alkuperäiset Pylint-tulokset

Pistemäärä: **8.79/10**, ilmoituksia yhteensä **85**. Koko tuloste: [docs/pylint/initial-output.txt](pylint/initial-output.txt).

| Tunnus | Ilmoitus | Määrä | Tiedostot |
|---|---|---|---|
| C0116 | missing-function-docstring | 73 | kaikki tiedostot |
| C0114 | missing-module-docstring | 4 | app.py, db.py, users.py, recipes.py |
| R0914 | too-many-locals | 3 | seed.py:92 (`make_recipe`), seed.py:137 (`main`), benchmark.py:125 (`main`) |
| R0911 | too-many-return-statements | 2 | app.py:89 (`recipe_form_error`), app.py:360 (`register`) |
| C0413 | wrong-import-position | 2 | benchmark.py:32–33 |
| R0801 | duplicate-code | 1 | users.py:33–38 ja recipes.py:56–61 |

## 4. Havaitut ongelmat

- **C0114 ja C0116 (docstring puuttuu).** Moduuleilla ja funktioilla ei ole docstring-kommentteja. Kurssin esimerkkisovelluksen tavoin funktioiden nimet kuvaavat niiden tehtävän (esimerkiksi `get_recipe_count`), ja vaikeammat kohdat on selitetty tavallisilla kommenteilla.
- **R0801 (toistuva koodi).** Reseptin makuluokituksen liittävä SQL-osa (`LEFT JOIN` makuluokkiin) oli kirjoitettu samanlaisena sekä reseptilistaan (`recipes.py`) että käyttäjäsivulle (`users.py`). Jos toista olisi muutettu, toinen olisi voinut jäädä vanhaksi. Tämä oli todellinen ylläpidettävyysongelma.
- **C0413 (import ei ole tiedoston alussa).** `benchmark.py` lisäsi projektin hakemiston hakupolkuun (`sys.path.insert`) ennen import-lauseita. Tämä oli turhaa, koska Python lisää ajettavan skriptin hakemiston hakupolkuun automaattisesti.
- **R0914 (liikaa paikallisia muuttujia).** Tiedostojen `seed.py` ja `benchmark.py` `main`-funktiot tekivät monta eri asiaa peräkkäin, joten ne olivat pitkiä ja vaikeasti luettavia. `make_recipe` luo yhden reseptin kaikki tiedot.
- **R0911 (liikaa return-lauseita).** `recipe_form_error` ja `register` tarkistavat lomakkeen kentät yksi kerrallaan ja palaavat heti ensimmäiseen virheeseen.

Pylint ei löytänyt käyttämättömiä importeja tai muuttujia, liian pitkiä rivejä, nimeämisvirheitä eikä varsinaisia ohjelmointivirheitä (E- tai W-luokan ilmoituksia).

## 5. Tehdyt korjaukset

- **Toistuva SQL (R0801).** Makuluokituksen liitos on nyt yhdessä vakiossa `recipes.TASTE_JOIN`, jota käyttävät sekä `recipes.search_conditions` että `users.get_recipes`. Kyselyjen tulos ei muuttunut.
- **Importit (C0413).** `benchmark.py`:stä poistettiin turha `sys.path.insert`, ja importit siirrettiin tiedoston alkuun.
- **Pitkät `main`-funktiot (R0914).**
  - `seed.py`: `main` jaettiin funktioihin `generate_rows`, `insert_rows` ja `print_summary`. Satunnaislukujen käyttöjärjestys ei muuttunut, joten sama siemen tuottaa edelleen täsmälleen samat tiedot.
  - `benchmark.py`: `main` jaettiin funktioihin `measure`, `print_plans` ja `print_results`.

Sovelluksen toimintaa, tietoturvaa, SQL-parametreja, transaktioita, malleja, CSS:ää ja tietokannan rakennetta ei muutettu.

## 6. Tulokset korjausten jälkeen

Pistemäärä: **8.80/10**, ilmoituksia yhteensä **86**. Koko tuloste: [docs/pylint/after-cleanup-output.txt](pylint/after-cleanup-output.txt).

| Tunnus | Ennen | Jälkeen |
|---|---|---|
| C0116 missing-function-docstring | 73 | 79 |
| C0114 missing-module-docstring | 4 | 4 |
| R0914 too-many-locals | 3 | 1 |
| R0911 too-many-return-statements | 2 | 2 |
| C0413 wrong-import-position | 2 | 0 |
| R0801 duplicate-code | 1 | 0 |
| **Yhteensä** | **85** | **86** |

Pistemäärä nousi vain vähän (8.79 → 8.80), vaikka kaikki todelliset ongelmat korjattiin. Syy on se, että lähes kaikki ilmoitukset ovat docstring-ilmoituksia. Pitkien funktioiden jakaminen pienempiin lisäsi kuusi uutta funktiota ja samalla kuusi uutta docstring-ilmoitusta.

Regressiotestit ajettiin erillisillä testitietokannoilla. Kaikki aiemmat testit (kirjautuminen, reseptien hallinta, oikeustarkistukset, CSRF, haku, suodatus, sivutus, käyttäjäsivut, arviot, luokittelut ja kissan ehdotukset) toimivat kuten ennen korjauksia. Lisäksi tarkistettiin, että `seed.py` tuottaa samalla siemenellä täsmälleen samat tiedot kuin ennen korjausta ja että `benchmark.py` toimii.

## 7. Jäljelle jääneet huomautukset

- **C0114 ja C0116 (83 kpl).** Docstring-kommentteja ei ole lisätty. Kurssin esimerkkisovelluksen tavoin sovelluksessa on tietoisesti käytetty kuvaavia funktioiden nimiä ja tarvittaessa tavallisia kommentteja. Päätös arvioidaan uudelleen ennen lopullista raporttia.
- **R0911 (2 kpl), `recipe_form_error` ja `register`.** Funktiot tarkistavat lomakkeen kentät järjestyksessä ja palauttavat ensimmäisen virheen. Varhaiset return-lauseet pitävät tarkistukset selkeinä, eikä niiden yhdistäminen tekisi koodista helpompaa lukea.
- **R0914 (1 kpl), `seed.make_recipe`.** Funktio luo yhden testireseptin nimen, ainekset, ohjeen, päivämäärän ja luokittelut. Muuttujat kuuluvat samaan peräkkäiseen tehtävään, ja funktio on vain testidatan luontiskriptissä.

## 8. Jatkotoimet ennen lopullista palautusta

- Ajetaan Pylint uudelleen sovelluksen lopullisesta versiosta samalla komennolla.
- Päätetään, lisätäänkö docstring-kommentit vai perustellaanko niiden puuttuminen lopullisessa raportissa.
- Korjataan mahdolliset uudet ilmoitukset tai perustellaan ne.
- Kirjoitetaan `pylint-report.md`, jossa on lopullinen Pylint-tuloste ja perustelu jokaiselle jäljelle jääneelle ilmoitukselle.

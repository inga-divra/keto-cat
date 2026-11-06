# Pylint-raportti

Tämä raportti on tehty sovelluksen lopullisesta versiosta. Se sisältää Pylintin tuloksen ja perustelun jokaiselle jäljelle jääneelle ilmoitukselle. Pylintin koko alkuperäinen tuloste on tiedostossa [docs/pylint/final-output.txt](docs/pylint/final-output.txt).

## 1. Ympäristö ja komento

- Päivämäärä: 6.11.2026
- Python 3.13.7 (koodi on tarkistettu myös Python 3.12:lla)
- Pylint 4.1.3 (astroid 4.3.4), oletusasetukset, ei omaa asetustiedostoa
- Pylint on vain kehitystyökalu, ei sovelluksen ajonaikainen riippuvuus.

Tarkastetut tiedostot ovat sovelluksen ja sen apuskriptien Python-tiedostot:

```
pip install pylint
pylint app.py db.py users.py recipes.py init_db.py seed.py benchmark.py
```

Mukana eivät ole virtuaaliympäristö, yksityinen `config.py`, mallitiedosto `config.example.py` (yksi asetusrivi), tietokannat eivätkä väliaikaiset testiskriptit.

## 2. Tulos

Pistemäärä: **8.80/10**

| Luokka | Tunnus | Ilmoitus | Määrä |
|---|---|---|---|
| Convention | C0116 | missing-function-docstring | 84 |
| Convention | C0114 | missing-module-docstring | 4 |
| Refactor | R0911 | too-many-return-statements | 2 |
| Refactor | R0914 | too-many-locals | 1 |
| **Yhteensä** | | | **91** |

- Docstring-ilmoituksia on 88 ja muita ilmoituksia 3.
- Virhe- (E) tai varoitusluokan (W) ilmoituksia ei ole. Pylint ei siis löytänyt esimerkiksi määrittelemättömiä nimiä, käyttämättömiä importteja tai muuttujia, vaarallisia oletusarvoja tai poikkeusten väärää käsittelyä.

## 3. Vertailu alustavaan tarkastukseen

Alustava tarkastus ([docs/pylint-initial-audit.md](docs/pylint-initial-audit.md)) tehtiin 5.11.2026 samalla Pylint-versiolla, samoilla asetuksilla ja samalla komennolla samoille tiedostoille. Tulokset ovat siksi vertailukelpoisia. Koodia on kuitenkin tarkastusten välillä lisätty: reseptilistan lisäsuodattimet, oma 403-sivu ja tunnisteiden tarkistus.

| | Alustava (ennen korjauksia) | Lopullinen |
|---|---|---|
| Pistemäärä | 8.79/10 | 8.80/10 |
| Ilmoituksia yhteensä | 85 | 91 |
| Docstring-ilmoituksia | 77 | 88 |
| Muita ilmoituksia | 8 | 3 |

Muut kuin docstring-ilmoitukset vähenivät 8:sta 3:een eli 62,5 %. Alustavassa tarkastuksessa korjattiin toistuva SQL-koodi (R0801), väärin sijoitetut importit (C0413) ja kaksi liian pitkää funktiota (R0914). Ilmoitusten kokonaismäärä kasvoi, koska uudet ominaisuudet ja pienemmiksi jaetut apufunktiot lisäsivät docstring-ilmoituksia. Pistemäärä pysyi lähes samana, koska Pylint laskee sen kaikista ilmoituksista, ja lähes kaikki ilmoitukset ovat docstring-ilmoituksia.

## 4. Docstring-ilmoitukset (88 kpl)

### Perustelu

Sovelluksessa ei käytetä docstring-kommentteja. Tämä on tietoinen päätös, joka noudattaa kurssin esimerkkisovelluksen tyyliä:

- Funktioiden nimet kertovat niiden tehtävän, esimerkiksi `get_recipe_count`, `check_csrf` ja `remove_comment`.
- Lähes kaikki funktiot ovat lyhyitä, ja niiden SQL-kyselyt tai Flask-reitit ovat luettavissa suoraan koodista.
- Kohdat, joiden toimintaa ei näe suoraan koodista, on selitetty tavallisilla kommenteilla. Esimerkkejä:
  - `read_catalog_filters` (`app.py:81`) selittää, miten virheelliset suodatinarvot käsitellään;
  - `search_conditions` (`recipes.py:54`) selittää, miksi `EXISTS` ei tuota samaa reseptiä useaan kertaan;
  - `MAX_ID` (`app.py`) selittää, miksi tunnisteet rajataan SQLiten 64-bittisiin kokonaislukuihin.
- Apuskripteillä `init_db.py`, `seed.py` ja `benchmark.py` on moduulin docstring, joka kertoo skriptin käyttötavan. Siksi niistä ei tule C0114-ilmoitusta.

Docstring-kommenttien lisääminen ei muuttaisi sovelluksen toimintaa eikä korjaisi virheitä, joten niitä ei lisätty pelkän pistemäärän vuoksi.

### C0114 missing-module-docstring (4 kpl)

`app.py:1`, `db.py:1`, `users.py:1`, `recipes.py:1`. Moduulien tehtävät näkyvät niiden nimistä: Flask-reitit, tietokantayhteys, käyttäjien ja reseptien SQL-kyselyt.

### C0116 missing-function-docstring (84 kpl)

**app.py (33 kpl)**
- Apufunktiot: `require_login` (47), `check_csrf` (51), `parse_id` (57), `get_own_recipe` (65), `get_class_groups` (73), `read_catalog_filters` (81), `catalog_args` (101), `read_page` (108), `empty_classes` (118), `group_recipe_classes` (121), `read_recipe_form` (128), `selected_class_ids` (141), `recipe_form_error` (144), `get_own_comment` (166), `read_comment_form` (174), `comment_form_error` (180), `render_recipe_page` (187), `add_csrf_token` (200).
- Virhesivut: `forbidden` (207), `page_not_found` (211).
- Reitit: `index` (215), `show_recipes` (235), `show_recipe` (287), `show_user` (294), `new_recipe` (305), `edit_recipe` (328), `delete_recipe` (355), `new_comment` (368), `edit_comment` (401), `delete_comment` (421), `register` (434), `login` (467), `logout` (491).

**db.py (4 kpl)**
- `get_connection` (4), `execute` (10), `last_insert_id` (21), `query` (24).

**users.py (6 kpl)**
- `create_user` (5), `check_login` (10), `get_user` (21), `get_recipe_count` (26), `get_recipes` (30), `get_comment_count` (39).

**recipes.py (20 kpl)**
- Luokittelut: `get_classes` (3), `get_class` (7), `get_recipe_classes` (12), `get_all_classes` (20), `add_recipe_classes` (28).
- Reseptit: `add_recipe` (33), `search_conditions` (54), `recipe_count` (84), `get_recipes` (88), `get_recipe` (98), `get_random_recipe` (107), `update_recipe` (119), `remove_recipe` (131).
- Arviot: `get_comments` (143), `get_rating` (151), `get_comment` (157), `has_comment` (166), `add_comment` (170), `update_comment` (175), `remove_comment` (179).

**init_db.py (1 kpl)**
- `main` (12).

**seed.py (9 kpl)**
- `parse_arguments` (58), `check_target` (70), `get_class_ids` (86), `make_recipe` (92), `make_reviews` (122), `generate_rows` (137), `insert_rows` (155), `print_summary` (170), `main` (178).

**benchmark.py (11 kpl)**
- `parse_arguments` (33), `check_source` (41), `make_copies` (65), `describe` (79), `query_plans` (87), `load_client` (94), `run_round` (102), `measure` (123), `print_plans` (144), `print_results` (150), `main` (158).

C0116-ilmoituksia on yhteensä 33 + 4 + 6 + 20 + 1 + 9 + 11 = 84. Kaikkien ilmoitusten jako tiedostoittain:

| Tiedosto | C0114 | C0116 | Muut | Yhteensä |
|---|---|---|---|---|
| app.py | 1 | 33 | 2 (R0911) | 36 |
| db.py | 1 | 4 | 0 | 5 |
| users.py | 1 | 6 | 0 | 7 |
| recipes.py | 1 | 20 | 0 | 21 |
| init_db.py | 0 | 1 | 0 | 1 |
| seed.py | 0 | 9 | 1 (R0914) | 10 |
| benchmark.py | 0 | 11 | 0 | 11 |
| **Yhteensä** | **4** | **84** | **3** | **91** |

## 5. Muut ilmoitukset (3 kpl)

### R0911 too-many-return-statements, `app.py:144` `recipe_form_error` (7/6)

Funktio tarkistaa reseptilomakkeen kentät järjestyksessä: otsikon, ainekset ja ohjeen pituuden sekä jokaisen luokitteluryhmän arvot. Se palauttaa ensimmäisen löytyneen virheen tekstinä tai `None`, jos lomake on kunnossa. Jokainen `return` vastaa yhtä selkeää virhetilannetta, ja käyttäjälle näytetään juuri sitä tilannetta koskeva viesti. Tarkistusten yhdistäminen yhteen ehtoon tai virhelistaan tekisi koodista vaikeamman lukea eikä muuttaisi toimintaa. Ilmoitus ei kerro virheestä.

### R0911 too-many-return-statements, `app.py:434` `register` (7/6)

Rekisteröitymisreitti käsittelee GET- ja POST-pyynnön ja tarkistaa käyttäjätunnuksen muodon, salasanan pituuden, salasanojen samuuden ja tunnuksen yksilöllisyyden. Jokaisen virheen jälkeen lomake näytetään uudelleen omalla virheilmoituksellaan, ja onnistuessa käyttäjä ohjataan kirjautumissivulle. Tämä on sama varhaisten paluiden rakenne kuin kurssin esimerkkisovelluksessa, ja se pitää jokaisen tarkistuksen ja sen viestin vierekkäin.

### R0914 too-many-locals, `seed.py:92` `make_recipe` (17/15)

Funktio on testidatan luontiskriptissä, ei itse sovelluksessa. Se luo yhden testireseptin: maun, nimen, ainekset, ohjeen, päivämäärän ja luokittelut. Muuttujat kuuluvat samaan peräkkäiseen tehtävään. Funktion jakaminen pienempiin osiin vaatisi monien arvojen välittämistä funktiolta toiselle. Lisäksi satunnaislukujen käyttöjärjestys ei saa muuttua, jotta sama siemen tuottaa jatkossakin täsmälleen saman testidatan, johon README:n mittaustulokset perustuvat.

## 6. Johtopäätös

Lopullisessa koodissa ei ole Pylintin virhe- eikä varoitusluokan ilmoituksia. Kaikki 91 ilmoitusta ovat tyyli- tai rakenneilmoituksia:

- 88 johtuu tietoisesta päätöksestä olla käyttämättä docstring-kommentteja;
- 3 on perusteltuja tapauksia, joissa koodin muuttaminen ei parantaisi luettavuutta.

Mikään jäljelle jäänyt ilmoitus ei osoita oikeellisuus-, tietoturva- tai ylläpidettävyysongelmaa. Alustavassa tarkastuksessa löytyneet todelliset ongelmat (toistuva SQL, importtien sijainti ja kaksi liian pitkää funktiota) on korjattu.

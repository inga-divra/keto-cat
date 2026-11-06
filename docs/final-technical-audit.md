# Tekninen valmiustarkastus

Tämä on sovelluksen teknisen valmiuden tarkastus ennen lopullista palautusta. Se ei ole kurssin vaatima lopullinen Pylint-raportti (`pylint-report.md`), joka tehdään erikseen sovelluksen lopullisesta versiosta.

## 1. Tarkastuksen tiedot

- Päivämäärä: 6.11.2026
- Tarkastettu versio: `9e174af` (main), työhakemisto puhdas tarkastuksen alussa
- Ympäristö: Windows 11, Python 3.13.7 (yhteensopivuus tarkistettu Python 3.12:lla), SQLite 3.50.4, Pylint 4.1.3
- Kaikki testit ajettiin erillisissä projektikopioissa ja väliaikaisissa tietokannoissa. Kehittäjän omaa `database.db`-tiedostoa ei avattu eikä muutettu (MD5-tarkiste sama ennen ja jälkeen).

Merkinnät: **PASS** = vaatimus täyttyy ja se on tarkistettu, **FAIL** = todettu puute, **MANUAL** = vaatii vielä käsin tehtävän tarkistuksen selaimessa.

## 2. Vaatimusten tarkistuslista

### Toiminnallisuus

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Rekisteröityminen, kirjautuminen ja uloskirjautuminen | PASS | `app.py:410–473`; testit: virheelliset tunnukset ja salasanat, kirjainkoosta riippumaton tunnuksen yksilöllisyys, uloskirjautuminen vain POST-pyynnöllä |
| Reseptin lisääminen, katselu, muokkaus ja poisto | PASS | `app.py:282–343`; luokittelu- ja arviotestit |
| Haku nimestä ja aineksista | PASS | `recipes.py:54–68` (`LIKE ? ESCAPE`); `%` ja `_` toimivat kirjaimellisesti |
| Julkiset käyttäjäsivut ja tilastot | PASS | `app.py:271–280`, `users.py`; reseptien ja kommenttien määrä lasketaan SQL:llä |
| Luokittelut Taste, Diet, Meal ja Restrictions | PASS | `init.sql`, `app.py:30–35`, `126–146`; väärän ryhmän tunnisteet hylätään |
| Lisäsuodattimet AND-ehdoilla | PASS | `recipes.py:75–81` (`EXISTS` jokaiselle valinnalle); 48 testiä, kaikki 240 luokitteluyhdistelmää |
| Arviot ja arvosanat, muokkaus ja poisto | PASS | `app.py:345–408`, `schema.sql:32–40` |
| Sivutus säilyttää haun ja kaikki suodattimet | PASS | `app.py:232–248`, `catalog_url`; seuraava-linkit tarkistettiin kaikilla sivuilla |
| Etusivun satunnainen Sweet/Savory-ehdotus | PASS | `app.py:192–210`; etusivulla ei hakua eikä lisäsuodattimia |

### Tekniset rajoitukset

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Python, Flask ja SQLite | PASS | `app.py`, `db.py` |
| Suorat parametrisoidut SQL-kyselyt, ei ORM:ää | PASS | kaikki käyttäjän arvot `?`-parametreina; ei `SELECT *` |
| Ei JavaScriptiä | PASS | ei `<script>`-tageja, `on*=`-attribuutteja eikä `javascript:`-linkkejä; lisäsuodattimet toteutettu `<details>`-elementillä |
| Ei muita ajonaikaisia kirjastoja kuin Flask riippuvuuksineen | PASS | importit: Flask, Werkzeug ja standardikirjasto; Pylint vain kehitystyökaluna |
| Itse kirjoitettu HTML ja CSS, ei käyttöliittymäkehyksiä | PASS | `static/main.css`, ei CSS-kehyksiä |
| Ulkoiset resurssit | Poikkeama, ks. kohta 8 | `templates/layout.html:8–10` lataa Pixelify Sans -fontin Google Fontsista |
| Koodi ja tietokannan nimet englanniksi | PASS | ei suomenkielisiä tunnisteita koodissa |
| Python 3.12 -yhteensopivuus | PASS | `py -3.12 -m py_compile` kaikille Python-tiedostoille |

### Tietoturva

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Salasanojen tiivisteet | PASS | `users.py:1–17`, Werkzeugin `generate_password_hash`; tietokannassa `scrypt:`-tiiviste |
| Istunnot ja tunnistautuminen | PASS | `session.clear()` ja uusi CSRF-tunniste kirjautuessa (`app.py:460–463`); evästeessä `HttpOnly` |
| CSRF-suojaus kaikissa tilaa muuttavissa pyynnöissä | PASS | `check_csrf` kaikissa POST-reiteissä; puuttuva, väärä tai toisen käyttäjän tunniste antaa 403 |
| Omistajuustarkistukset palvelimella | PASS | `get_own_recipe`, `get_own_comment`; vieras, toinen käyttäjä ja reseptin tekijä saavat vieraan arvion muokkauksesta 403 |
| Syötteiden tarkistus ja pituusrajat | PASS | otsikko 100, ainekset 3000, ohje 5000, kommentti 1000, haku 100, tunnus 3–20, salasana 8–128 merkkiä |
| SQL-injektiot | PASS | parametrit; testattu `' OR 1=1 --` |
| Jinja-mallien merkintöjen koodaus | PASS | ei `|safe`- tai `Markup`-käyttöä; HTML ja `<script>` näkyvät tekstinä otsikoissa, aineksissa ja arvioissa |
| Suorat URL-osoitteet | PASS | kielletyt GET- ja POST-pyynnöt antavat 403 eivätkä muuta tietoja |
| Puuttuvat ja virheelliset tunnisteet | **FAIL** | tavalliset virheelliset tunnisteet antavat 404, mutta yli 64-bittiset luvut antavat 500 (ks. S1) |
| Johdonmukaiset HTTP-tilakoodit | Osittain | 403, 404 ja 405 oikein; ks. S1 ja L1 |
| Tietokantayhteydet ja transaktiot | PASS | `db.py:10–29` (`finally`), `recipes.py:33–140` (yksi yhteys ja yksi commit) |
| Ei salaisuuksia tai yksityisiä tietokantoja Gitissä | PASS | `config.py`, `*.db` ja `test-data/` ohitetaan; ks. L4 historiasta |
| Ei arkaluonteisia tietoja dokumentaatiossa | PASS | ei paikallisia polkuja tai sähköpostiosoitteita versionhallinnassa; `seedpassword` on dokumentoitu testikäyttäjien salasana |

### Koodin laatu ja tietokannan rakenne

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Kuvaavat snake_case-nimet, neljän välilyönnin sisennys | PASS | ei sarkaimia |
| Rivien pituus | PASS | ei yli 100 merkin rivejä |
| Ei käyttämätöntä koodia tai importteja | PASS | Pylint ei raportoi W-luokan ilmoituksia |
| Ei `SELECT *` | PASS | haettu koko projektista |
| NOT NULL-, UNIQUE-, CHECK- ja REFERENCES-rajoitteet | PASS | `schema.sql`; testattu: tuntematon käyttäjä, tuntematon luokka, arvosana 0 ja tuntematon resepti hylätään |
| Viiteavaimet ja poistaminen | PASS | `PRAGMA foreign_keys = ON` (`db.py:6`); reseptin poisto poistaa luokittelut ja arviot transaktiossa, lisäksi `ON DELETE CASCADE` |
| Ei N+1-kyselyjä | PASS | luettelo, reseptisivu ja käyttäjäsivu tekevät kiinteän määrän kyselyjä |
| Ei turhaa toistuvaa SQL:ää | PASS | `TASTE_JOIN` ja `search_conditions` yhteisinä |
| Selkeät funktiot | PASS | Pylint: 8.81/10, ei E- tai W-ilmoituksia, 3 perusteltua R-ilmoitusta (`docs/pylint-initial-audit.md`) |

### Saavutettavuus ja käytettävyys

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Lomakekentillä `<label>` | PASS | automaattinen tarkistus 7 sivulla: jokaisella näkyvällä kentällä on oma `<label for>` |
| Kuvien `alt`-tekstit | PASS | sovelluksessa ei ole `<img>`-elementtejä; kissa on CSS-piirros, jolla on `aria-hidden="true"`; README-kuvilla on alt-tekstit |
| `<fieldset>` ja `<legend>` ryhmille | PASS | luokittelut, arvosana ja lisäsuodattimet |
| Näppäimistökäyttö | MANUAL | vain tavallisia linkkejä, painikkeita ja `<details>`-elementtejä; tarkistettava selaimessa |
| Näkyvä kohdistus | MANUAL | CSS ei poista `outline`-reunusta; `summary` saa oman kohdistustyylin |
| Otsikkorakenne | PASS | jokaisella sivulla yksi `h1` (logo), sivun otsikko `h2`, osiot `h3`/`h4` |
| Rivinvaihdot säilyvät | PASS | `.recipe-text { white-space: pre-wrap }` aineksille, ohjeille ja arvioille |
| Responsiivisuus ilman vaakavieritystä | **FAIL** | tavallinen sisältö toimii 320 px:n leveydellä, mutta pitkä välilyönnitön sana reseptin nimessä aiheuttaa vaakavierityksen (ks. U1) |
| Selkeät virheilmoitukset | PASS | lomakevirheet näytetään ja syötteet säilyvät |
| Navigointi, tyhjät tilat ja virhesivut | Osittain | kissa-aiheiset tyhjät tilat ja oma 404-sivu; 403 näyttää Flaskin oletussivun (L1) |

### Arvosanan 5 suorituskykyvaatimukset

| Vaatimus | Tila | Näyttö |
|---|---|---|
| Sivutus | PASS | 10 reseptiä sivulla, 1 000 sivua suurella aineistolla |
| Suuri testiaineisto `seed.py`:llä | PASS | 100 käyttäjää, 10 000 reseptiä, 20 000 arviota, toistettava siemen |
| Mittaus `benchmark.py`:llä | PASS | toimii, kieltäytyy käyttämästä `database.db`:tä |
| Mitattavasti hyödyllinen indeksi | PASS | `idx_recipes_user`; `SCAN` → `SEARCH`, käyttäjäsivu noin 2,2–2,3 kertaa nopeampi |
| Toistettavat ja paikkansapitävät tulokset README:ssä | PASS | mittausmenetelmä, komennot ja vaihtelun selitys dokumentoitu |

## 3. Tietoturvahavainnot

Kriittisiä tai korkean vakavuuden havaintoja ei löytynyt.

**Keskitaso**

- **S1. Liian suuret tunnisteet aiheuttavat palvelinvirheen 500.** Flaskin `<int:...>`-muunnin ja `request.args.get(..., type=int)` hyväksyvät mielivaltaisen suuren luvun, mutta SQLite tallentaa vain 64-bittisiä kokonaislukuja. Esimerkiksi `/recipe/9223372036854775808` antaa `OverflowError: Python int too large to convert to SQLite INTEGER` ja tilakoodin 500, kun taas `/recipe/9223372036854775807` antaa oikein 404. Varmistettu kahdeksassa kohdassa: `/recipe/<id>`, `/user/<id>`, `/edit_recipe/<id>`, `/delete_recipe/<id>`, `/edit_comment/<id>`, `/delete_comment/<id>`, etusivun `previous`-parametri ja `/new_comment`-lomakkeen `recipe_id`. Tietoja ei vuoda eikä muutu, mutta virhe rikkoo johdonmukaisen 404-käsittelyn. Ehdotettu korjaus: reittien muuntimeen raja, esimerkiksi `<int(max=9223372036854775807):recipe_id>`, ja sama yläraja lomake- ja kyselyparametreille.

**Matala**

- **L1. Oletusvirhesivut.** 403, 400 ja 405 näyttävät Flaskin englanninkielisen oletussivun ilman sovelluksen ulkoasua. Esimerkiksi kirjautumaton käyttäjä saa 403-sivun avatessaan `/new_recipe`. Ehdotus: `@app.errorhandler(403)` samaan tyyliin kuin 404-sivu, ja mahdollisesti linkki kirjautumiseen.
- **L2. Puuttuvat lomakekentät antavat 400.** Väärennetty POST ilman kenttiä (esimerkiksi ilman `title`- tai `username`-kenttää) antaa 400 Bad Request, ei palvelinvirhettä. Toiminta on turvallinen; sen voi halutessaan muuttaa ystävällisemmäksi.
- **L3. Istuntoevästeeltä puuttuu `SameSite`.** Evästeessä on `HttpOnly; Path=/`. CSRF-tunnisteet suojaavat lomakkeet jo nyt, mutta `app.config["SESSION_COOKIE_SAMESITE"] = "Lax"` olisi lisäsuoja. CSRF-tunnisteen vertailu tehdään tavallisella `!=`-vertailulla; `secrets.compare_digest` olisi varovaisempi, mutta käytännön riski on hyvin pieni.
- **L4. Vanha avain Git-historiassa.** Commitissa `6d20b4c` (2.11.2026) `config.example.py` sisälsi oikealta näyttävän avaimen, ja commit on GitHubissa. Avain korvattiin myöhemmin paikkamerkillä, eikä sitä käytetä paikallisessa `config.py`:ssä. Toimenpidettä ei tarvita, kunhan julkaistussa sovelluksessa ei koskaan käytetä tätä avainta.

## 4. Toiminnallisuus- ja käytettävyyshavainnot

- **U1. Pitkät sanat rikkovat kapean asettelun (keskitaso).** Reseptin nimi on enintään 100 merkkiä, mutta välilyönnitön nimi ei rivity. 320 px:n leveydellä reseptisivun `<h2>`-otsikko ja reseptiluettelon linkki ylittävät reunan ja aiheuttavat vaakavierityksen. Ainekset, ohjeet ja arviot rivittyvät oikein (`overflow-wrap: anywhere`). Ehdotus: `overflow-wrap: anywhere` myös otsikoille ja reseptiluettelon linkeille.
- **U2. Kirjautumaton käyttäjä saa 403-sivun (matala).** Suora siirtyminen osoitteeseen `/new_recipe` ilman kirjautumista näyttää oletusvirhesivun. Navigaatio ei näytä linkkiä kirjautumattomille, joten tilanne syntyy vain kirjoittamalla osoite itse.
- **U3. Käyttäjäsivun reseptiluetteloa ei ole sivutettu (tieto).** Suurella aineistolla sivulla on noin 100 reseptiä, ja sivu latautuu indeksin kanssa noin 5–10 ms:ssa. Ei vaadi toimenpiteitä.

## 5. Regressiotestien tulokset

Testit ovat kehitysvaiheen tarkistusskriptejä väliaikaisessa hakemistossa. Ne eivät ole osa repositoriota.

| Testijoukko | Tulos | Huomio |
|---|---|---|
| Luokittelut | 49/49 | korjattu testin virhe, ks. alla |
| Arviot ja arvosanat | 62/62 | |
| Sivutus | 56/56 | |
| Lisäsuodattimet | 48/48 | |
| Suuri aineisto (10 000 reseptiä) | 21/21 | |
| Käyttäjäsivut | 28/28 | korjattu kaksi vanhentunutta tekstiä, ks. alla |
| Tämän tarkastuksen testit | 86/94 | 8 epäonnistumista = havainto S1 |
| **Yhteensä** | **350/358** | |

**Luokittelutestin aiempi epäonnistuminen (48/49).** Testi `empty title rejected` oli virheellinen. Apufunktio `bad()` lähetti otsikon "Keep me <b>", mutta testin lisäkentät korvasivat sen tyhjällä otsikolla ennen lähetystä. Sovellus palautti oikein tyhjän kentän ja virheilmoituksen, mutta testi odotti kentässä arvoa, jota ei koskaan lähetetty. Testi korjattiin odottamaan lähetettyä arvoa, eikä sovellusta muutettu. Tulos on nyt 49/49.

**Käyttäjäsivujen testi (26/28 ennen korjausta).** Kaksi tarkistusta odotti vanhentuneita merkkijonoja: Jinja ei koodaa mallin omaa tekstiä, joten `hasn't` ei näy muodossa `hasn&#39;t`, ja tervehdys oli tarkoituksella muutettu muotoon "Welcome to alice's corner of the café." Testit korjattiin; sovellusta ei muutettu.

**Tämän tarkastuksen testit kattavat:**
- vieraan, reseptin tekijän, arvioijan ja ulkopuolisen käyttäjän oikeudet kaikissa muokkaus- ja poistoreiteissä;
- CSRF-tunnisteen puuttumisen, väärän tunnisteen ja toisen käyttäjän tunnisteen;
- erikoismerkit, HTML:n ja emojit otsikoissa, aineksissa ja arvioissa;
- liian pitkät syötteet ja virheelliset käyttäjätunnukset;
- puuttuvat ja liian suuret tunnisteet;
- tyhjän tietokannan;
- viiteavaimet ja poistot;
- lomakkeiden `label`-elementit, `fieldset`- ja `legend`-parit sekä `h1`-otsikot.

**Käsin tarkistettu kuvakaappauksin:** työpöytä sekä 320 ja 375 px:n leveys.

## 6. Tietokanta ja suorituskyky

- Tuore asennus: `git clone` → `config.py` mallista → `python init_db.py` luo 5 taulua, 11 luokittelua neljässä ryhmässä ja indeksin `idx_recipes_user`. Sovellus käynnistyy ilman `database.db`-tiedostoa repositoriossa.
- Rajoitteet ja viiteavaimet toimivat. `PRAGMA integrity_check` ja `PRAGMA foreign_key_check` eivät löytäneet virheitä testien jälkeen.
- Indeksi `idx_recipes_user` muuttaa käyttäjäsivun kyselysuunnitelman (`SCAN recipes` → `SEARCH ... USING INDEX`), ja mittaukset ovat toistettavissa `benchmark.py`:llä. README:n tulokset vastaavat mitattuja arvoja, ja vaihtelu on selitetty.
- Tunnetut rajat on dokumentoitu README:ssä: `LIKE '%sana%'`, `COUNT(*)` jokaisella sivulla, `OFFSET` kaukaisilla sivuilla ja `ORDER BY RANDOM()`.

## 7. GitHub-valmius

- Kaikki asennukseen tarvittavat tiedostot ovat versionhallinnassa.
- `database.db`, `config.py`, `.venv/` ja `test-data/` ohitetaan `.gitignore`:lla, ja `CLAUDE.md` ohitetaan paikallisesti.
- README:n asennuskomennot vastaavat projektia, ja tuore kloonaus testattiin.
- Kaikki README:n kuvat ja linkit (`keto-cat-home.png`, `pylint-audit.svg`, `sqlite-performance.svg`, `docs/pylint-initial-audit.md`) osoittavat olemassa oleviin tiedostoihin.
- README ei sisällä vanhentuneita suunniteltujen ominaisuuksien lupauksia. Maininta kehitysvaiheesta on jo poistettu, eikä README väitä, että reseptikuvia voisi lisätä.

## 8. Poikkeamat rajoituksista

- **Google Fonts (`templates/layout.html:8–10`).** Logo ja painikkeet käyttävät Pixelify Sans -fonttia, joka ladataan Googlen palvelimelta. Kyseessä ei ole JavaScript eikä käyttöliittymäkehys, mutta se on ulkoinen palvelu ja lähettää kävijän IP-osoitteen Googlelle. Projektin omissa ohjeissa ulkoisia palveluja vältetään ja grafiikka tallennetaan paikallisesti. Sovellus toimii ilman fonttia, koska CSS:ssä on varafontti `"Courier New", monospace`. Vaihtoehdot: fontin tallentaminen omaksi tiedostoksi (lisenssi sallii, koska fontti on avoin OFL-fontti) tai pelkkä varafontti.

Muita poikkeamia kurssin rajoituksista ei löytynyt.

## 9. Suositellut korjaukset tärkeysjärjestyksessä

1. **S1:** rajoitetaan tunnisteet 64-bittisiin lukuihin, jotta liian suuret arvot antavat 404 eivätkä 500.
2. **U1:** lisätään `overflow-wrap: anywhere` reseptin otsikolle ja reseptiluettelon linkeille.
3. **Kohta 8:** päätetään Google Fonts -fontin käytöstä (paikallinen fonttitiedosto tai varafontti).
4. **L1:** oma 403-virhesivu samaan tyyliin kuin 404-sivu.
5. **L3:** `SESSION_COOKIE_SAMESITE = "Lax"` ja `secrets.compare_digest` CSRF-vertailuun.
6. Lopullinen Pylint-ajo ja `pylint-report.md` lopullisesta versiosta.

## 10. Käsin tehtävät tarkistukset

- Näppäimistöllä läpikäynti oikeassa selaimessa: kaikki linkit, painikkeet, valintanapit, valintaruudut ja `Advanced filters` -osio (Enter/välilyönti).
- Kohdistuksen näkyvyys kaikissa ohjaimissa, myös keltaisilla painikkeilla.
- Ruudunlukijalla: arvosanan tähtien piilotus (`aria-hidden`) ja numeroarvon lukeminen, sivutuksen `aria-current` sekä virheilmoitukset.
- Mobiilinäkymä oikealla puhelimella tai selaimen kehitystyökaluilla, U1-korjauksen jälkeen.
- SVG-kaavioiden näkyminen GitHubin README-sivulla.
- Lopullinen Pylint-raportti ja kurssin vertaisarvioinnit (opiskelija tekee itse).

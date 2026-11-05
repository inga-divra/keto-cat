# Keto-cat

![Keto-Cat Café -sovelluksen etusivu: pikselitaidekissa kysyy, tekeekö mieli makeaa vai suolaista](docs/images/keto-cat-home.png)

Sovelluksessa käyttäjät pystyvät jakamaan keto- ja LCHF-reseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje. Sovelluksen kissa auttaa valitsemaan, mitä tehdä: käyttäjä kertoo, tekeekö mieli suolaista vai makeaa, ja kissa ehdottaa sopivaa reseptiä.

Sovelluksen käyttöliittymä on englanninkielinen. Käyttäjät voivat kuitenkin kirjoittaa reseptinsä millä kielellä tahansa.

Tässä pääasiallinen tietokohde on resepti ja toissijainen tietokohde on kommentti reseptiin.

## Toteutetut ominaisuudet

- Käyttäjä pystyy luomaan tunnuksen, kirjautumaan sisään ja kirjautumaan ulos.
- Käyttäjä pystyy lisäämään keto- ja LCHF-reseptejä sekä muokkaamaan ja poistamaan omia reseptejään.
- Kaikki käyttäjät, myös kirjautumattomat, näkevät eri käyttäjien lisäämät reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla. Haku kohdistuu reseptin nimeen ja aineksiin.
- Reseptilistan voi suodattaa maun perusteella, ja suodatusta voi käyttää yhdessä haun kanssa.
- Etusivun pikselitaidekissa ehdottaa satunnaisen reseptin käyttäjän valitseman maun perusteella.

### Reseptien luokittelut

Käyttäjä luokittelee reseptin sitä lisätessään tai muokatessaan. Luokittelujen vaihtoehdot on tallennettu tietokantaan.

- Maku (Taste): Sweet tai Savory. Pakollinen, yksi vaihtoehto.
- Ruokavalio (Diet): Keto tai LCHF. Vapaaehtoinen, yksi vaihtoehto.
- Ateria (Meal): Breakfast, Main course, Snack tai Dessert. Vapaaehtoinen, yksi vaihtoehto.
- Erityisruokavalio (Restrictions): Dairy-free, Egg-free ja Nut-free. Vapaaehtoinen, vaihtoehtoja voi valita useita.

Vapaaehtoisia luokitteluja voi muuttaa tai poistaa reseptiä muokattaessa. Maku on aina valittava. Reseptin sivulla näytetään kaikki sen luokittelut.

### Käyttäjäsivut

- Jokaisella käyttäjällä on julkinen käyttäjäsivu, joka näyttää käyttäjän julkaisemien reseptien määrän, listan niistä ja käyttäjän kirjoittamien kommenttien määrän.
- Reseptin tekijän ja kommentin kirjoittajan nimestä pääsee hänen käyttäjäsivulleen.

### Kommentit ja arvosanat

- Kirjautunut käyttäjä voi kirjoittaa toisen käyttäjän reseptiin arvion, jossa on kommentti ja pakollinen arvosana 1–5.
- Käyttäjä voi antaa samalle reseptille vain yhden arvion, eikä hän voi arvioida omaa reseptiään.
- Käyttäjä voi muokata ja poistaa omia arvioitaan.
- Kaikki, myös kirjautumattomat käyttäjät, näkevät arviot. Reseptin sivulla näytetään arvosanojen keskiarvo ja määrä.
- Kun resepti poistetaan, myös sen arviot poistetaan.

## Suunnitellut ominaisuudet

Nämä ominaisuudet eivät ole vielä valmiita:

- Reseptilistan sivutus.
- Reseptilistan suodatus ruokavalion, aterian ja erityisruokavalion perusteella.
- Reseptikuvat.

## Sovelluksen käynnistäminen

Sovellus käyttää Pythonia (yhteensopiva Python 3.12:n kanssa), Flaskia ja SQLiteä. Muita kirjastoja ei tarvita.

Komennot ajetaan projektin juurihakemistossa. Windowsissa komennot on tarkoitettu PowerShelliin. Linuxissa ja macOS:ssä käytetään yleensä komentoa `python3` komennon `python` sijaan.

1. Kloonaa repositorio ja siirry sen hakemistoon:

   ```
   git clone https://github.com/inga-divra/keto-cat.git
   cd keto-cat
   ```

2. Luo virtuaaliympäristö ja aktivoi se.

   Windows (PowerShell):

   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Jos PowerShell estää aktivointiskriptin, salli se nykyisessä ikkunassa komennolla `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` ja aja aktivointi uudelleen.

   Linux ja macOS:

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Asenna Flask:

   ```
   pip install flask
   ```

4. Luo asetustiedosto `config.py` mallitiedoston `config.example.py` pohjalta.

   Windows (PowerShell):

   ```
   Copy-Item config.example.py config.py
   ```

   Linux ja macOS:

   ```
   cp config.example.py config.py
   ```

5. Luo satunnainen salainen avain:

   ```
   python -c "import secrets; print(secrets.token_hex(16))"
   ```

   Avaa `config.py` tekstieditorissa ja korvaa arvo `change-this-secret-key` tulostetulla avaimella. Tiedostoa `config.py` ei lisätä versionhallintaan.

6. Luo tietokanta `database.db`:

   ```
   python init_db.py
   ```

   Skripti luo tietokannan tiedostojen `schema.sql` (taulut) ja `init.sql` (kaikkien neljän luokitteluryhmän vaihtoehdot: Taste, Diet, Meal ja Restrictions) perusteella. Jos `database.db` on jo olemassa, skripti kysyy ennen sen poistamista. Vastaa `yes` vain, jos haluat aloittaa tyhjästä tietokannasta.

7. Käynnistä sovellus:

   ```
   flask run
   ```

8. Avaa selaimessa osoite http://127.0.0.1:5000.

Kun palaat myöhemmin projektin pariin, riittää aktivoida virtuaaliympäristö ja ajaa `flask run`.

## Sovelluksen testaaminen

Juuri luodussa tietokannassa ei ole käyttäjiä eikä reseptejä. Siksi testaus aloitetaan luomalla tunnukset ja lisäämällä reseptit.

1. Luo kaksi tunnusta sivulla **Register**, esimerkiksi `alice` ja `bob`. Käyttäjätunnuksessa on 3–20 merkkiä (kirjaimet, numerot, `-` ja `_`), ja salasanassa on vähintään 8 merkkiä.
2. Kirjaudu sisään ensimmäisellä tunnuksella sivulla **Log in**.
3. Lisää sivulla **Add recipe** kaksi reseptiä:
   - Ensimmäiselle maku **Sweet**, ruokavalio (**Diet**), ateria (**Meal**) ja useampi erityisruokavalio (**Restrictions**), esimerkiksi **Dairy-free** ja **Nut-free**.
   - Toiselle vain maku **Savory**. Jätä ruokavalioksi ja ateriaksi **Not specified** ja erityisruokavaliot valitsematta.

   Voit kirjoittaa aineksiin ja ohjeeseen useita rivejä, ja rivinvaihdot näkyvät reseptin sivulla. Reseptin sivulla näkyvät kaikki valitut luokittelut. Omassa reseptissä ei ole arviolomaketta, koska omaa reseptiä ei voi arvioida.
4. Avaa sivu **Recipes**. Siinä näkyvät kaikkien käyttäjien reseptit, niiden maku, lisääjä ja lisäyspäivä.
5. Kirjoita hakukenttään sana, joka esiintyy reseptin nimessä tai aineksissa, ja paina **Search**. **Clear** tyhjentää haun.
6. Suodata reseptejä painikkeilla **Sweet**, **Savory** ja **All recipes**. Suodatus toimii myös yhdessä haun kanssa.
7. Palaa etusivulle (**Home**) ja valitse **Sweet** tai **Savory**. Kissa ehdottaa satunnaista reseptiä, ja **Show me another** pyytää uuden ehdotuksen.
8. Avaa ensimmäinen resepti ja valitse **Edit**. Aiemmat luokittelut ovat valmiiksi valittuina. Vaihda ateria, poista ruokavalio valitsemalla **Not specified** ja poista yksi erityisruokavalio. Tallenna ja tarkista muutokset reseptin sivulta.
9. Avaa toinen resepti ja valitse **Delete**. Poisto pyytää vielä vahvistuksen.
10. Kirjaudu ulos, kirjaudu sisään toisella tunnuksella ja avaa ensimmäisen käyttäjän resepti. Muokkaus- ja poistolinkkejä ei näytetä. Jos kirjoitat osoiteriville suoraan `/edit_recipe/<id>` tai `/delete_recipe/<id>` toisen käyttäjän reseptin tunnisteella, sovellus palauttaa virheen 403 (Forbidden).
11. Kirjoita samaan reseptiin arvio kohdassa **Leave a review**: valitse arvosana 1–5, kirjoita kommentti ja paina **Send review**. Arvio näkyy reseptin sivulla, ja sivulla näkyvät arvosanojen keskiarvo ja määrä. Lomake katoaa, koska samaan reseptiin voi antaa vain yhden arvion.
12. Muokkaa arviota linkistä **Edit review** ja vaihda arvosana. Keskiarvo päivittyy. Kokeile myös **Delete review**: poisto pyytää vahvistuksen, ja sen jälkeen voit kirjoittaa arvion uudelleen. Jätä lopuksi yksi arvio reseptiin. Avaa sen **Edit review** -linkki ja kirjoita muistiin osoiterivillä näkyvä osoite, esimerkiksi `/edit_comment/1`.
13. Paina arvion kirjoittajan nimeä. Käyttäjäsivulla näkyvät kohdat **Published recipes** ja **Comments written**. Avaa myös ensimmäisen käyttäjän sivu reseptin tekijän nimestä ja tarkista, että reseptien määrä ja lista ovat oikein.
14. Kirjaudu ulos ja kirjaudu sisään ensimmäisellä tunnuksella. Toisen käyttäjän arviossa ei ole muokkaus- ja poistolinkkejä. Jos kirjoitat osoiteriville suoraan kohdassa 12 muistiin kirjoitetun osoitteen `/edit_comment/<id>` tai `/delete_comment/<id>`, sovellus palauttaa virheen 403 (Forbidden).
15. Kirjaudu ulos painikkeella **Log out** ja avaa resepti kirjautumattomana. Arviot, keskiarvo ja käyttäjäsivut näkyvät, ja arviolomakkeen tilalla on linkki **Log in**.

## Nykyiset rajoitukset

- Sovellus on vielä kehitysvaiheessa.
- Reseptikuvia ei vielä voi lisätä.
- Reseptilistassa ei ole vielä sivutusta.
- Reseptilistan voi suodattaa vain maun perusteella. Muut luokittelut näkyvät reseptin sivulla, mutta niillä ei voi vielä suodattaa.

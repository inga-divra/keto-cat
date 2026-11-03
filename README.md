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
- Reseptin lisäämisen yhteydessä valitaan maku: makea (Sweet) tai suolainen (Savory). Maut on tallennettu tietokantaan.
- Reseptilistan voi suodattaa maun perusteella, ja suodatusta voi käyttää yhdessä haun kanssa.
- Etusivun pikselitaidekissa ehdottaa satunnaisen reseptin käyttäjän valitseman maun perusteella.

## Suunnitellut ominaisuudet

Nämä ominaisuudet eivät ole vielä valmiita:

- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja montako kommenttia hän on kirjoittanut, sekä listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy valitsemaan reseptille maun lisäksi muita luokitteluja, esimerkiksi:
  - Ruokavalio: keto tai LCHF
  - Ateria: aamiainen, pääruoka, välipala tai jälkiruoka
  - Erityisruokavalio: maidoton, kananmunaton tai pähkinätön
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.
- Reseptilistan sivutus.
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

   Skripti luo tietokannan tiedostojen `schema.sql` (taulut) ja `init.sql` (makuluokittelut Sweet ja Savory) perusteella. Jos `database.db` on jo olemassa, skripti kysyy ennen sen poistamista. Vastaa `yes` vain, jos haluat aloittaa tyhjästä tietokannasta.

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
3. Lisää sivulla **Add recipe** kaksi reseptiä: toiselle maku **Sweet** ja toiselle **Savory**. Voit kirjoittaa aineksiin ja ohjeeseen useita rivejä, ja rivinvaihdot näkyvät reseptin sivulla.
4. Avaa sivu **Recipes**. Siinä näkyvät kaikkien käyttäjien reseptit, niiden maku, lisääjä ja lisäyspäivä.
5. Kirjoita hakukenttään sana, joka esiintyy reseptin nimessä tai aineksissa, ja paina **Search**. **Clear** tyhjentää haun.
6. Suodata reseptejä painikkeilla **Sweet**, **Savory** ja **All recipes**. Suodatus toimii myös yhdessä haun kanssa.
7. Palaa etusivulle (**Home**) ja valitse **Sweet** tai **Savory**. Kissa ehdottaa satunnaista reseptiä, ja **Show me another** pyytää uuden ehdotuksen.
8. Avaa oma resepti ja kokeile linkkejä **Edit** ja **Delete**. Poisto pyytää vielä vahvistuksen.
9. Kirjaudu ulos, kirjaudu sisään toisella tunnuksella ja avaa ensimmäisen käyttäjän resepti. Muokkaus- ja poistolinkkejä ei näytetä. Jos kirjoitat osoiteriville suoraan `/edit_recipe/<id>` tai `/delete_recipe/<id>` toisen käyttäjän reseptin tunnisteella, sovellus palauttaa virheen 403 (Forbidden).
10. Kirjaudu ulos painikkeella **Log out**.

## Nykyiset rajoitukset

- Sovellus on vielä kehitysvaiheessa.
- Reseptikuvia ei vielä voi lisätä.
- Käyttäjäsivut, kommentit ja arvosanat ovat suunnitteilla.
- Reseptillä on toistaiseksi vain yksi luokittelu, maku.
- Reseptilistassa ei ole vielä sivutusta.

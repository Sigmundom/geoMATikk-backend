# GIB2 Kodeskjellet
Dette er et kodeskjellet for GIB2 prosjektet. Det inneholder en del grunnleggende innstillinger
som kan være til hjelp i prosjektet. Det er ikke et krav om å bruke det, men erfaringsmessig vil det hjelpe
dere som er noe usikre på hvordan man lager nettsider. Det vil også være lettere for stud.ass å kunne hjelpe 
dere da dette vi være kjent for han/hun.

Oppsettet dere får er basert på Flask, som er et enkelt system for å håndtere oppsett av nettsider. Det
er python basert, og bruker dette språket til å kjøre backenden. Flask kan knyttes opp til å bruke mange 
ulike database løsninger, men denne guiden vil bruke postgresql og den medfølgende postgis
installasjonen, da den burde gi dere hva dere trenger for å løse prosjektoppgaven.

Stegene under må gjøres for å kunne kjøre flask:

1. Lag et python virtuelt miljø (virtualenv), med navn venv og plassert i prosjektmappen. Venv er en instans av python, 
og gjør det det mulig å installere ulike tillegspakker i python, uten at andre prosjekter
blir påvirket. God praksis er at det alltid er et eget venv for hvert prosjekt man jobber på.

2. Naviger til prosjektmappen og kjør ```source venv/bin/activate ```  for å aktivere venv.

3. Kjør kommandoene under for å hente de siste oppdateringene til programvaren. Pip er pythons
utvidelsesbibliotek, og er stedet der man henter ulike datapakker man trenger. Kommandoen som kjøres etterpå
henter de distribusjonene man trenger og installerer dem i venv, slik at prosjektet kjører. (og gjør at dere slipper 
å installere hver enkelt manuelt på hver pc dere jobber på...)
    ```
    pip install --upgrade pip
    pip install -r requirements.txt
    ```


4. for å starte server, installer postgresql med følgende verdier
    ``` 
    user = postgres
    password = password
    databasename = postgres
    port = 5432
    host = localhost
    ```
5. Installer postgis extension til postgresql server
når den er installert, gå til serveren, høyreklikk og velg query tools og kjør
    ```
    create extension postgis;
    ```

6. set System variables
    ``` 
    APP_SETTINGS="config.DevelopmentConfig"
    DATABASE_URL="postgresql://localhost/beacons"
    
    ```
Standard praksis for å jobbe med dette videre ved hjelp av Git. Har beskrevet de vanligste kommandoene under.
Link til dokumentasjon: https://git-scm.com/docs/gittutorial/2.23.0
```
git checkout "branchname" - Bytter til branchen man vil jobbe på
git pull - henter siste oppdateringer på denne branchen
```
Når ferdig med hva man jobber med og man har skjekket at det fungerer!!
```
git pull - henter den siste oppdateringen på branchen, i tilfelle andre jobber 
samtidig på den. Dersom det er en merge conflict mellom hva dere har gjort, MÅ den løses
før man sender over egne endringer.
git add . - legger til alle endringer
git commit -m "Beskrivelse av task" - beskriver hva man har gjort
git push --set-upstream origin <tasknavn> - Sender denne informasjonen til git, slik at andre kan få jobbe med det. 
Siste delen av kommandoen er hva som må skrives inn første gang man commiter til en ny branch.
```

Til slutt, her er en rekke linker til dokumentasjon som kan være nyttig i prosjektet:

```
https://www.python.org/dev/peps/pep-0008/ -Hvordan skrive god kode
```
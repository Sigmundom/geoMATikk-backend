# Hvordan initalisere databasen
## Last ned alt
Følg den vanlige guiden å last ned alt som trengs

## Initialiser databasen
Pass på at du er i et venv og kjør:
* flask db upgrade
* flask db migrate

## Last inn restaurantdataene
Følg punktene i denne rekkefølgen
* cd data
* flask shell
* from data.init_db import init
* init()
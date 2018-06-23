# Veřejná data z projektu oadvokatech.ospravedlnosti.cz

Tento dataset obsahuje data o konečných rozhodnutích
Nejvyššího, Nejvyššího správního a Ústavního soudu, jejichž neautentická znění
jsou bezplatně dostupná na webech [nsoud.cz](http://nsoud.cz),
[nssoud.cz](http://nssoud.cz) a [usoud.cz](http://usoud.cz), odkud je
pravidelně stahujeme. Více o projektu a práci s daty najdete na [našich
stránkách](https://{HOST}/about).

# Popis formátu dat

Dataset obsahuje 3 CSV soubory (jako oddělovač je ovšem použit středník):

- strukturovaná data o advokátech tak, jak jsou dostupná na stránkách [České
  advokátní komory](http://www.cak.cz/) ({ADVOCATE_NUM} advokátů)
- data o případech obsahující mimo jiné i přiřazení konkrétnímu advokátovi
  a rozhodnutí soudu ({CASE_NUM} případů)
- data o dokumentech obsahujících rozhodnutí ({DOCUMENT_NUM} dokumentů)

## Advokáti

| Sloupec               | Popis                          |
|-----------------------|--------------------------------|
| id                    | Interní identifikátor          |
| identification_number | Identifikační číslo osoby      |
| registration_number   | Evidenční číslo                |
| degree_after          | Titul za jménem                |
| degree_before         | Titul před jménem              |
| name                  | Křestní jméno                  |
| surname               | Příjmení                       |

**Poznámky**:

- IČO, jméno a tituly se u advokáta mohou teoreticky měnit v čase. Zde je k
  dispozici pouze poslední známý stav.
- Evidenční číslo by mělo být neměnné.

## Případy

| Sloupec       | Popis                                             |
|---------------|---------------------------------------------------|
| id            | Interní identifikátor                             |
| court_id      | Identifikátor soudu                               |
| registry_sign | Spisová značka                                    |
| year          | Rok                                               |
| case_result   | Výsledné rozhodnutí                               |
| advocate_id   | Identifikátor advokáta (interní)                  |
| annuled       | Indikátor (0 nebo 1), zda byl daný případ zrušen. |
| annuling_case | Identifikátor případu, který daný zrušil          |

**Poznámky**:

- Pokud není k danému případu přiřazen advokát, je `advocate_id` nastaveno na
  -1.

### Identifikátor soudu

| Identifikátor          | Soud             |
|------------------------|------------------|
| constitutional         | Ústavní          |
| supreme                | Nejvyšší         |
| supreme_administrative | Nejvyšší správní |


### Výsledné rozhodnutí

| Identifikátor | Popis                                                                                                  |
|---------------|--------------------------------------------------------------------------------------------------------|
| positive      | meritorní konečné rozhodnutí (to znamená, že se jeho podáním soud alespoň zčásti co do obsahu zabýval) |
| neutral       | rozhodnutí o zastavení řízení (to znamená, že podání bylo pravděpodobně vzato zpět)                    |
| negative      | nemeritorní konečné rozhodnutí (to znamená, že se jeho podáním soud co do obsahu vůbec nezabýval)      |

## Dokumenty

| Sloupec       | Popis                                                        |
|---------------|--------------------------------------------------------------|
| id            | Interní identifikátor                                        |
| case_id       | Identifikátor případu (interní)                              |
| court_id      | Identifikátor příslušného soudu                              |
| decision_date | Datum rozhodnutí                                             |
| local_path    | Cesta k dokumentu směřující do uložiště dokumentů            |
| url_original  | Adresa, ze které byl dokument získán                         |
| url_proxy     | Adresa, kde je dokument k dispozici v rámci našeho projektu  |

Poznámky:

- u některých dokumentů již jejich původní adresa není platná

## Informace k dokumentům specifické pro jednotlivé soudy

Jednotlivé CSV soubory obsahují sloupec `document_id`, pomocí něhož se dají
tyto informace spárovat s dokumenty uvedenými výše.

### Ústavní soud

| Sloupec                       | Popis                                                        |
|-------------------------------|--------------------------------------------------------------|
| ecli                          | Identifikátor ECLI                                           |
| form_decision                 | Forma rozhodnutí                                             |
| decision_result               | Výsledek rozhodnutí                                          |
| parallel_reference_laws       | Paralelní citace (Sbírka zákonů)                             |
| parallel_reference_judgements | Paralelní citace (Sbírka nálezů a usnesení)                  |
| popular_title                 | Populární název                                              |
| decision_date                 | Datum rozhodnutí                                             |
| delivery_date                 | Datum vyhlášení                                              |
| filing_date                   | Datum podání                                                 |
| publication_date              | Datum zpřístupnění                                           |
| proceedings_type              | Typ řízení                                                   |
| importance                    | Význam                                                       |
| proposer                      | Navrhovatel                                                  |
| institution_concerned         | Dotčený orgán                                                |
| justice_rapporteur            | Soudce zpravodaj                                             |
| contested_act                 | Napadený akt                                                 |
| concerned_laws                | Dotčené ústavní zákony a mezinárodní smlouvy                 |
| concerned_other               | Ostatní dotčené předpisy                                     |
| dissenting_opinion            | Odlišné stanovisko                                           |
| proceedings_subject           | Předmět řízení                                               |
| subject_index                 | Věcný rejstřík                                               |
| ruling_language               | Jazyk rozhodnutí                                             |
| note                          | Poznámka                                                     |

### Nejvyšší soud

| Sloupec                       | Popis                                                        |
|-------------------------------|--------------------------------------------------------------|
| ecli                          | Identifikátor ECLI                                           |
| decision_type                 | Typ rozhodnutí                                               |

### Nejvyšší správní soud

| Sloupec                       | Popis                                                        |
|-------------------------------|--------------------------------------------------------------|
| order_number                  | Číslo jednací                                                |
| decision_type                 | Forma rozhodnutí                                             |
| decision                      | Rozhodnutí                                                   |
| sides                         | Účastníci řízení                                             |
| prejudicate                   | Prejudikatura                                                |
| complaint                     | Opravný prostředek/stížnost                                  |

 ---

 Poslední změna: {LAST_UPDATE}

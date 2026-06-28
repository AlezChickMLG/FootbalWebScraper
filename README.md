# Fluxul complet al scraperului

## 1. Pornirea aplicației

```python
web_scraper = FlashscoreWebScraper()

web_scraper.process_info({
    "team": "Spania"
})
```

---

## 2. `process_info(info)`

### Parametru

```python
info = {
    "team": "Spania"
}
```

### Flux

```
process_info(info)
        │
        ▼
reset_page()
        │
        ▼
get_team_url("Spania")
        │
        ▼
goto(Pagina echipei)
        │
        ▼
goto(Tab "Rezultate")
        │
        ▼
get_all_matches()
        │
        ▼
Pentru fiecare meci
        │
        ▼
goto(Pagina meciului)
        │
        ▼
goto(Tab "Statistici")
        │
        ▼
get_statistics()
        │
        ▼
write_to_file()
```

---

# Metode

## `reset_page()`

Navighează către pagina principală.

```python
self.page.goto(self.flashscore_url)
```

### URL

```
https://www.flashscore.ro/
```

### Return

```
None
```

---

## `get_team_url(team)`

Primește numele echipei și caută în bara de căutare.

```python
team_url = self.get_team_url("Spania")
```

Navighează doar în cadrul paginii principale.

### Return

Exemplu:

```python
"/echipa/spania/n5tbN10K/"
```

sau

```python
None
```

dacă echipa nu există.

sau

```python
False
```

dacă apare o excepție.

---

## Construirea URL-ului echipei

```python
full_team_url = (
    f"{self.flashscore_url}{team_url}"
)
```

Exemplu:

```
https://www.flashscore.ro/
+
/echipa/spania/n5tbN10K/

↓

https://www.flashscore.ro/echipa/spania/n5tbN10K/
```

---

## Pagina rezultatelor

Din pagina echipei se extrage:

```python
results_href = results_href_element.get_attribute("href")
```

Exemplu:

```python
"/echipa/spania/n5tbN10K/rezultate/"
```

URL final:

```python
result_url = (
    f"{self.flashscore_url_no_slash}{results_href}"
)
```

↓

```
https://www.flashscore.ro/echipa/spania/n5tbN10K/rezultate/
```

---

## `get_all_matches()`

Extrage toate meciurile.

Pentru fiecare meci se citesc:

```python
home_team
away_team
start_time
match_url
```

### Return

```python
[
    {
        "home_team": "Spania",
        "away_team": "Franța",
        "start_time": "05.06.2025",
        "match_url": "/meci/YgYxK6r9/"
    },
    {
        ...
    }
]
```

---

## Pagina unui meci

```python
self.page.goto(match["match_url"])
```

Exemplu:

```
https://www.flashscore.ro/meci/YgYxK6r9/
```

---

## Pagina statisticilor

Din pagina meciului:

```python
button_href = statistics_button.get_attribute("href")
```

Exemplu:

```python
"/meci/YgYxK6r9/#/statistici-meci/statistici"
```

Navigare:

```python
self.page.goto(
    f"{self.flashscore_url_no_slash}{button_href}"
)
```

↓

```
https://www.flashscore.ro/meci/YgYxK6r9/#/statistici-meci/statistici
```

---

## `get_statistics()`

Extrage toate statisticile.

Returnează:

```python
{
    "Posesie minge": {
        "Posesie": {
            "home": "62%",
            "away": "38%"
        }
    },
    "Șuturi": {
        "Șuturi pe poartă": {
            "home": "8",
            "away": "3"
        }
    }
}
```

---

## `write_to_file(team, match, statistics)`

Scrie statisticile în:

```
output/
└── Spania/
    └── Spania-Franța|05.06.2025
```

Formatul fișierului:

```
Posesie minge

Posesie: 62% | 38%

Șuturi

Șuturi pe poartă: 8 | 3
Șuturi: 14 | 9
...
```

Return:

```
None
```

---

# Flux complet

```
process_info()

        │
        ▼

reset_page()

        │
        ▼

https://www.flashscore.ro/

        │
        ▼

get_team_url("Spania")

        │
        ├── return "/echipa/spania/n5tbN10K/"
        ▼

https://www.flashscore.ro/echipa/spania/n5tbN10K/

        │
        ▼

Pagina "Rezultate"

        │
        ▼

get_all_matches()

        │
        ├── return [
        │       {
        │         home_team,
        │         away_team,
        │         start_time,
        │         match_url
        │       }
        │   ]
        ▼

Pagina meciului

        │
        ▼

Pagina "Statistici"

        │
        ▼

get_statistics()

        │
        ├── return {
        │      categorie:
        │          statistici
        │   }
        ▼

write_to_file()

        │
        ▼

output/<echipa>/<meci>
```
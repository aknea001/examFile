# Exam File
---
## Du trenger:
* Python [Download here](https://www.python.org/downloads/)
* GitHub Desktop [Download here]("https://desktop.github.com/download/)
---
## Hvordan laste ned
* Åpne GitHub Desktop og logg inn
* Trykk på "File" og "Clone Repository..."
![clone Repo img](https://github.com/aknea001/examFile/blob/main/imgs/cloneRepo.png?raw=true)

* Trykk på URL og lim inn "https://github.com/aknea001/examFile.git" i den første boksen, i den andre boksen velger du hvor prosjektet skal bli lastet ned (Skriv ned Local Pathen)
![clone URL img](https://github.com/aknea001/examFile/blob/main/imgs/cloneUrl.png?raw=true)

* Åpne ett terminal vindu (cmd på windows) og skriv inn
```
cd [Din Path hvor du lastet ned prosjektet]
```

* For å laste ned moduler brukt skriver du i terminalen  
Mac:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r req.txt
deactivate
```
Windows:
```
python3 -m venv .venv
.\.venv\Scripts\activate
pip install -r req.txt
deactivate
```
  
  
* For å starte appen skriv  
Mac:
```
source .venv/bin/activate
cd frontend
python main.py
```
Windows:
```
.\.venv\Scripts\activate
cd frontend
python main.py
```
---
## Hvordan bruke exam file
* Registrer ved å trykke på "Create account" og skriv inn brukernavn og passord og trykk på "Register"  
![register img](https://github.com/aknea001/examFile/blob/main/imgs/register.png?raw=true)

* Etter det logg inn med samme brukernavn og passord

### Lasting opp og ned filer
* For å laste opp filer trykker du på "Upload" og velger filen
* For å laste ned trykker du på "Download" ved siden av den filen du vil laste ned
![register img](https://github.com/aknea001/examFile/blob/main/imgs/downloadUpload.png?raw=true)
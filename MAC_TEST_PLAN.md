---
name: Shortcut Mac Test Plan
description: Piano test shortcut Spese su Mac — tutto il contesto per testare senza ripetere errori
type: project
---

## Contesto

Shortcut "Spese" per iPhone: tracker spese automatico con Apple Pay.
Repo: `ludovez93/iphone-shortcuts`, release attuale: v7.5

## Cosa funziona (testato su iPhone)
- Regex Replace Text: testato, funziona (categorizza merchant → Cibo/Trasporti/etc.)
- File append con WFTextTokenString: testato, funziona ("test scrittura file 123" scritto e letto)
- Riepilogo viewer: funziona, mostra il contenuto del file
- Automazione Wallet: triggera lo shortcut (notifica arriva)

## Cosa NON funziona
- Il file Spese.txt NON viene creato quando lo shortcut gira dall'automazione Wallet
- Non sappiamo se il Wallet Transaction trigger passa dati (Amount, Merchant) come ExtensionInput
- Non sappiamo se detect.number/gettext su ExtensionInput funzionano con dati Wallet

## Bug risolti durante lo sviluppo
1. If/Else plist: WFInput per ExtensionInput richiede `Type:Variable + Variable` wrapper — MA il blocco If/Else è stato eliminato del tutto
2. file.append: parametro `WFFileAppendService` non esiste → deve essere `WFFileStorageService`
3. file.append: `WFFilePath` deve essere wrappato in WFTextTokenString, non stringa piatta
4. file.append: `WFInput` deve usare WFTextTokenString (non WFTextTokenAttachment) per funzionare
5. Replace Text: parametri corretti sono `WFReplaceTextFind`, `WFReplaceTextReplace`, `WFReplaceTextRegularExpression`, `WFReplaceTextCaseSensitive`

## Cosa testare su Mac

### Test 1: Verifica che lo shortcut si installa e gira
```bash
# Clona il repo
git clone https://github.com/ludovez93/iphone-shortcuts.git
cd iphone-shortcuts

# Installa lo shortcut (macOS Shortcuts app)
open Spese-signed.shortcut
# Oppure:
# shortcuts import Spese-signed.shortcut

# Eseguilo
shortcuts run "Spese"
# Verifica se crea Spese.txt in iCloud Drive
```

### Test 2: Verifica struttura plist
```bash
# Dumpa il plist e verifica ogni azione
python3 -c "
import plistlib, json
with open('Spese-signed.shortcut', 'rb') as f:
    # Il file firmato potrebbe non essere leggibile con plistlib
    # Usa il file non firmato:
    pass

with open('Spese.shortcut', 'rb') as f:
    data = plistlib.load(f)
    for i, a in enumerate(data['WFWorkflowActions']):
        print(f'{i}: {a[\"WFWorkflowActionIdentifier\"]}')"
```

### Test 3: Confronta con shortcut creato manualmente
1. Su Mac, apri Comandi Rapidi
2. Crea manualmente uno shortcut con: Text "test" → Append to File → Notification
3. Esportalo come file
4. Confronta il plist con quello generato da Python

### Test 4: Crea shortcut manualmente con If/Else
1. Su Mac, crea: If [Shortcut Input has any value] → Alert "SI" → Otherwise → Alert "NO"
2. Esporta
3. Leggi il plist per vedere il formato ESATTO del condizionale

### Test 5: Simula input Wallet
```bash
# Prova a passare input allo shortcut
echo "Bar Roma 12.50" | shortcuts run "Spese" -i -
# Verifica se Spese.txt viene creato con dati
```

## File sorgente
- `Spese_source.py` — genera Spese.shortcut (tracker automatico)
- `Riepilogo_source.py` — genera Riepilogo.shortcut (viewer/editor)
- Firma via: POST https://hubsign.routinehub.services/sign (body: {"shortcut": "XML plist"})
- Python: usa plistlib per generare binary plist

## Architettura shortcut Spese v7.5
1. detect.number da ExtensionInput → importo
2. gettext da ExtensionInput → esercente
3. 6x Replace Text regex (catena) → categoria (Cibo/Trasporti/Abbigliamento/Svago/Bollette/Altro)
4. Date + Format Date (dd/MM/yyyy e HH:mm)
5. Componi riga leggibile: "data ora | esercente | categoria | €importo"
6. Append a Spese.txt (iCloud root)
7. Componi riga CSV: "data,ora,esercente,categoria,importo"
8. Append a Spese.csv (iCloud root)
9. Notifica

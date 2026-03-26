# Cosa fare sul Mac

## Prima cosa: apri Terminale

Lo trovi in Applicazioni → Utility → Terminale

## Passo 1: Installa Node.js (se non c'è)

Scrivi nel terminale:
```
node --version
```
Se dà errore, vai su https://nodejs.org e scarica la versione LTS. Installa.

## Passo 2: Installa Claude Code

```
npm install -g @anthropic-ai/claude-code
```

Ti chiederà di fare login con il tuo account Anthropic.

## Passo 3: Scarica il progetto

```
git clone https://github.com/ludovez93/iphone-shortcuts.git
cd iphone-shortcuts
```

## Passo 4: Lancia Claude

```
claude
```

## Passo 5: Copia e incolla questo messaggio a Claude

```
Leggi il file MAC_TEST_PLAN.md in questa cartella.

Contiene tutto il contesto di un progetto shortcut iPhone che non riesco a testare da Windows.
Devi:
1. Installare Spese-signed.shortcut su questo Mac
2. Eseguirlo con: shortcuts run "Spese"
3. Verificare se crea Spese.txt in iCloud Drive
4. Se non funziona, aprire Comandi Rapidi su Mac, creare MANUALMENTE uno shortcut identico (Text → Append to File), esportarlo, e confrontare il plist con quello generato da Python per trovare le differenze
5. Fixare il codice Python (Spese_source.py), rigenerare, firmare, e pushare su GitHub

Tutto il contesto dei bug trovati è nel MAC_TEST_PLAN.md. Leggilo prima di iniziare.
```

## Passo 6: Lascia fare a Claude

Claude leggerà il piano, testerà tutto, e pusherà la versione corretta su GitHub.

## Passo 7: Torna sull'iPhone

Vai su https://github.com/ludovez93/iphone-shortcuts/releases e scarica la nuova versione.

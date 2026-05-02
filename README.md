# Quantum Inspired Cipher

Un piccolo algoritmo di crittografia in Python ispirato al quantum computing.

L'idea e didattica: usa una chiave, genera una sequenza pseudo-casuale di
"basi di misura", mescola le posizioni dei byte e applica una maschera che
ricorda una scelta fra basi computazionali e basi ruotate.

Non e crittografia professionale e non deve proteggere dati reali. Per quello
servono librerie verificate come `cryptography`, AES-GCM o ChaCha20-Poly1305.

## Uso

```bash
python3 quantum_cipher.py encrypt "Messaggio segreto" --key "la-mia-chiave"
```

Il comando stampa un token cifrato. Per decifrarlo:

```bash
python3 quantum_cipher.py decrypt "TOKEN" --key "la-mia-chiave"
```

## Cosa c'entra il quantum computing

- **Qubit simulati**: la maschera nasce da flussi chiamati `raw-qubits` e
  `phase-qubits`.
- **Basi di misura**: ogni bit della maschera viene scelto da una base
  pseudo-casuale, simile nell'ispirazione ai protocolli tipo BB84.
- **Trascrizione di misura**: il testo viene permutato con una sequenza
  deterministica generata dalla chiave.
- **Integrita**: un tag HMAC rileva chiavi sbagliate o modifiche al token.

## Mini esempio in codice

```python
from quantum_cipher import QuantumInspiredCipher

cipher = QuantumInspiredCipher("la-mia-chiave")
token = cipher.encrypt("Ciao universo quantistico")
print(token)
print(cipher.decrypt(token))
```

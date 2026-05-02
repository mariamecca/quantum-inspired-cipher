# Quantum Inspired Cipher

A small educational Python cipher inspired by quantum computing.

The idea is educational: it uses a secret key, generates a pseudo-random
sequence of "measurement bases", shuffles byte positions, and applies a mask
that resembles a choice between computational and rotated bases.

This is not professional cryptography and should not be used to protect real
data. For that, use audited libraries and standards such as `cryptography`,
AES-GCM, or ChaCha20-Poly1305.

## Usage

```bash
python3 quantum_cipher.py encrypt "Secret message" --key "my-secret-key"
```

The command prints an encrypted token. To decrypt it:

```bash
python3 quantum_cipher.py decrypt "TOKEN" --key "my-secret-key"
```

## Quantum Computing Inspiration

- **Simulated qubits**: the mask is generated from streams called `raw-qubits`
  and `phase-qubits`.
- **Measurement bases**: each bit of the mask is selected through a
  pseudo-random basis, loosely inspired by protocols such as BB84.
- **Measurement transcript**: the text is permuted using a deterministic
  sequence generated from the key.
- **Integrity**: an HMAC tag detects wrong keys or modified tokens.

## Mini Code Example

```python
from quantum_cipher import QuantumInspiredCipher

cipher = QuantumInspiredCipher("my-secret-key")
token = cipher.encrypt("Hello quantum universe")
print(token)
print(cipher.decrypt(token))
```

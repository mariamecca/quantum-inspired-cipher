#!/usr/bin/env python3
"""
Quantum-inspired educational cipher.

This is a toy algorithm for learning. It borrows ideas from quantum computing
vocabulary (bases, phase masks, measurement schedules), but it is not a
replacement for audited cryptography such as AES-GCM, ChaCha20-Poly1305, or
real quantum key distribution protocols.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import secrets
import sys
from dataclasses import dataclass


MAGIC = b"QIC1"
NONCE_SIZE = 16
TAG_SIZE = 16


def _shake(seed: bytes, label: bytes, size: int) -> bytes:
    return hashlib.shake_256(seed + b"|" + label).digest(size)


def _derive_seed(password: str, nonce: bytes) -> bytes:
    if not password:
        raise ValueError("La chiave non puo essere vuota.")
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        b"quantum-inspired-cipher|" + nonce,
        200_000,
        dklen=32,
    )


def _xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def _quantum_mask(seed: bytes, size: int) -> bytes:
    """
    Build a reversible mask with a BB84-like schedule.

    basis bit 0: use the raw stream bit.
    basis bit 1: use the phase stream bit, as if measuring in a rotated basis.
    """
    raw = _shake(seed, b"raw-qubits", size)
    phase = _shake(seed, b"phase-qubits", size)
    basis = _shake(seed, b"measurement-bases", size)

    return bytes((r & ~b) | (p & b) for r, p, b in zip(raw, phase, basis))


def _permutation(seed: bytes, size: int) -> list[int]:
    """
    Deterministically shuffle byte positions from the key seed.

    The repeated hash blocks act like a pseudo-random measurement transcript.
    """
    order = list(range(size))
    transcript = _shake(seed, b"measurement-transcript", max(1, size * 8))
    cursor = 0

    for i in range(size - 1, 0, -1):
        if cursor + 8 > len(transcript):
            transcript += _shake(
                seed,
                b"measurement-transcript-extra" + cursor.to_bytes(8, "big"),
                size * 4,
            )
        pick = int.from_bytes(transcript[cursor : cursor + 8], "big") % (i + 1)
        cursor += 8
        order[i], order[pick] = order[pick], order[i]

    return order


def _apply_permutation(data: bytes, order: list[int]) -> bytes:
    out = bytearray(len(data))
    for source, target in enumerate(order):
        out[target] = data[source]
    return bytes(out)


def _reverse_permutation(data: bytes, order: list[int]) -> bytes:
    out = bytearray(len(data))
    for source, target in enumerate(order):
        out[source] = data[target]
    return bytes(out)


@dataclass(frozen=True)
class QuantumInspiredCipher:
    password: str

    def encrypt(self, message: str) -> str:
        plaintext = message.encode("utf-8")
        nonce = secrets.token_bytes(NONCE_SIZE)
        seed = _derive_seed(self.password, nonce)

        mask = _quantum_mask(seed, len(plaintext))
        scrambled = _apply_permutation(plaintext, _permutation(seed, len(plaintext)))
        ciphertext = _xor_bytes(scrambled, mask)

        header = MAGIC + nonce + ciphertext
        tag = hmac.new(_shake(seed, b"auth-key", 32), header, hashlib.sha256).digest()[:TAG_SIZE]
        return base64.urlsafe_b64encode(header + tag).decode("ascii")

    def decrypt(self, token: str) -> str:
        try:
            packet = base64.urlsafe_b64decode(token.encode("ascii"))
        except Exception as exc:
            raise ValueError("Token non valido: non e base64 corretto.") from exc

        min_size = len(MAGIC) + NONCE_SIZE + TAG_SIZE
        if len(packet) < min_size or packet[: len(MAGIC)] != MAGIC:
            raise ValueError("Token non valido o formato non riconosciuto.")

        nonce_start = len(MAGIC)
        nonce_end = nonce_start + NONCE_SIZE
        nonce = packet[nonce_start:nonce_end]
        ciphertext = packet[nonce_end:-TAG_SIZE]
        received_tag = packet[-TAG_SIZE:]

        seed = _derive_seed(self.password, nonce)
        header = packet[:-TAG_SIZE]
        expected_tag = hmac.new(_shake(seed, b"auth-key", 32), header, hashlib.sha256).digest()[:TAG_SIZE]
        if not hmac.compare_digest(received_tag, expected_tag):
            raise ValueError("Chiave errata o messaggio alterato.")

        mask = _quantum_mask(seed, len(ciphertext))
        scrambled = _xor_bytes(ciphertext, mask)
        plaintext = _reverse_permutation(scrambled, _permutation(seed, len(ciphertext)))
        return plaintext.decode("utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cifrario didattico ispirato al quantum computing.")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Operazione da eseguire.")
    parser.add_argument("text", help="Testo in chiaro oppure token cifrato.")
    parser.add_argument("-k", "--key", required=True, help="Chiave segreta/password.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    cipher = QuantumInspiredCipher(args.key)

    try:
        if args.mode == "encrypt":
            print(cipher.encrypt(args.text))
        else:
            print(cipher.decrypt(args.text))
    except ValueError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

import unittest
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa

from apps.modules.cipherlab.services import CipherService


class LegacyCipherCompatibilityTests(unittest.TestCase):
    def test_caesar_uses_legacy_character_arithmetic(self):
        self.assertEqual(CipherService.operate("caesar", "encrypt", "Meet Me At Six AM ", parameter="3"), "PhhwWPhWDwWVlaWDPW")

    def test_caesar_85_character_demo(self):
        self.assertEqual(CipherService.operate("caesar_ascii", "encrypt", "abcxyz"), "fgh234")

    def test_monoalphabetic_matches_java_substitution_table(self):
        self.assertEqual(CipherService.operate("monoalphabetic", "encrypt", "abcxyz"), "QWEBNM")

    def test_vigenere_encrypt_and_decrypt_alpha_characters(self):
        encrypted = CipherService.operate("vigenere", "encrypt", "the second offic!", key="MATH")
        self.assertEqual(encrypted, "FHXZQCHUPOYMUC")
        self.assertEqual(CipherService.operate("vigenere", "decrypt", encrypted, key="MATH"), "THESECOND OFFIC".replace(" ", ""))

    def test_rot13_preserves_non_latin_letters(self):
        self.assertEqual(CipherService.operate("rot13", "encrypt", "Hello, Cipher! مرحبا"), "Uryyb, Pvcure! مرحبا")

    def test_legacy_atbash_menu_item_is_shift_by_two(self):
        self.assertEqual(CipherService.operate("atbash", "encrypt", "abc"), "cde")

    def test_rail_fence_uses_column_fill_not_zigzag(self):
        encrypted = CipherService.operate("rail_fence", "encrypt", "abcdef", parameter="3")
        self.assertEqual(encrypted, "adbecf")
        self.assertEqual(CipherService.operate("rail_fence", "decrypt", encrypted, parameter="3"), "abcdef")

    def test_rail_fence_drops_tail_as_the_java_matrix_does(self):
        self.assertEqual(CipherService.operate("rail_fence", "encrypt", "abcde", parameter="3"), "abc")

    def test_vernam_one_time_pad_round_trip(self):
        encrypted = CipherService.operate("vernam", "encrypt", "attackatdawn", key="lemonlemonle")
        self.assertEqual(CipherService.operate("vernam", "decrypt", encrypted, key="lemonlemonle"), "attackatdawn")

    def test_seeded_vernam_stream_is_reproducible(self):
        first = CipherService.operate("vernam_random", "encrypt", "Hello")
        second = CipherService.operate("vernam_random", "encrypt", "Hello")
        self.assertEqual(first, "ZXUIG")
        self.assertEqual(second, first)

    def test_legacy_binary_mask_round_trip_for_seven_bit_text(self):
        encrypted = CipherService.operate("otp_binary", "encrypt", "A")
        self.assertEqual(encrypted, "0010100 ")
        self.assertEqual(CipherService.operate("otp_binary", "decrypt", encrypted), "A")

    def test_xor_shares_recombine(self):
        shares = CipherService.operate("xor_shares", "encrypt", "legacy demo", parameter="3")
        self.assertEqual(CipherService.operate("xor_shares", "decrypt", shares), "legacy demo")

    def test_rsa_signed_big_integer_byte_format(self):
        encrypted = CipherService.operate("rsa", "encrypt", "A", key="e=17,n=3233")
        self.assertEqual(encrypted, "CuY=")
        self.assertEqual(CipherService.operate("rsa", "decrypt", encrypted, key="d=2753,n=3233"), "A")

    def test_dsa_sha1_der_sign_and_verify(self):
        private_key = dsa.generate_private_key(key_size=1024)
        private_der = private_key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        public_der = private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        signature = CipherService.operate(
            "dsa", "encrypt", "legacy message", key=base64.b64encode(private_der).decode()
        )
        verified = CipherService.operate(
            "dsa",
            "decrypt",
            "legacy message",
            key=base64.b64encode(public_der).decode(),
            parameter=signature,
        )
        self.assertEqual(verified, "true")

    def test_des_uses_fixed_legacy_iv_and_round_trips(self):
        ciphertext = CipherService.operate("des", "encrypt", "legacy DES", key="12345678")
        self.assertEqual(CipherService.operate("des", "decrypt", ciphertext, key="12345678"), "legacy DES")

    def test_hill_round_trip_with_invertible_key(self):
        encrypted = CipherService.operate("hill", "encrypt", "help", key="gybnqkurp")
        self.assertEqual(encrypted, "tfjpnw")
        self.assertEqual(CipherService.operate("hill", "decrypt", encrypted, key="gybnqkurp"), "helpxx")

    def test_playfair_round_trip_for_valid_pairs(self):
        encrypted = CipherService.operate("playfair", "encrypt", "hidethegoldx", key="playfairexample")
        self.assertEqual(encrypted, "bmodzbxdnage")
        self.assertEqual(CipherService.operate("playfair", "decrypt", encrypted, key="playfairexample"), "hidethegoldx")


if __name__ == "__main__":
    unittest.main()
"""Python ports of the algorithms shipped in the legacy PEncrypt sources."""

import base64
import math
import secrets


class LegacyCipherError(ValueError):
    """Raised when legacy algorithm parameters or ciphertext are invalid."""


class CipherService:
    ALGORITHMS = {
        "caesar": "Caesar",
        "caesar_ascii": "Caesar (85-character alphabet)",
        "monoalphabetic": "Monoalphabetic",
        "vigenere": "Vigenere",
        "rail_fence": "Rail Fence",
        "playfair": "Playfair",
        "hill": "Hill",
        "atbash": "Atbash (+2 legacy shift)",
        "rot13": "ROT13",
        "vernam": "Vernam (one-time pad)",
        "vernam_random": "Vernam (seeded Java stream)",
        "otp_binary": "OneTimePad (legacy binary XOR)",
        "des": "DES-CBC (legacy)",
        "rsa": "RSA (legacy textbook format)",
        "dsa": "DSA / SHA1withDSA",
        "xor_shares": "XOR secret shares",
    }

    _MONO_FROM = "abcdefghijklmnopqrstuvwxyz"
    _MONO_TO = "QWERTYUIOPASDFGHJKLZXCVBNM"
    _CAESAR_85 = (
        "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&()"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/[]{}=<>?_"
    )
    _DES_IV = bytes((11, 22, 33, 44, 99, 88, 77, 66))

    @classmethod
    def operate(cls, algorithm, operation, text, *, key="", parameter=""):
        if algorithm not in cls.ALGORITHMS:
            raise LegacyCipherError("الخوارزمية غير معروفة")
        if operation not in ("encrypt", "decrypt"):
            raise LegacyCipherError("العملية يجب أن تكون encrypt أو decrypt")
        decrypt = operation == "decrypt"
        method = getattr(cls, f"_{algorithm}")
        return method(text, decrypt=decrypt, key=key, parameter=parameter)

    @staticmethod
    def _java_remainder(number, divisor):
        return number - math.trunc(number / divisor) * divisor

    @classmethod
    def _caesar(cls, text, *, decrypt, key, parameter):
        try:
            shift = int(parameter or 3) * (-1 if decrypt else 1)
        except (TypeError, ValueError) as exc:
            raise LegacyCipherError("إزاحة قيصر يجب أن تكون رقماً صحيحاً") from exc
        result = []
        for char in text:
            base = ord("A") if char.isupper() else ord("a")
            code = cls._java_remainder(ord(char) + shift - base, 26) + base
            result.append(chr(code))
        return "".join(result)

    @classmethod
    def _caesar_ascii(cls, text, *, decrypt, key, parameter):
        result = []
        for char in text:
            try:
                index = cls._CAESAR_85.index(char)
            except ValueError:
                result.append(char)
            else:
                if decrypt:
                    output_index = index - 5 if index >= 5 else 81 + index
                else:
                    output_index = index + 5 if index <= 80 else index - 81
                if output_index >= len(cls._CAESAR_85):
                    raise LegacyCipherError("خوارزمية Caesar ذات الأبجدية 85 تتجاوز حدود المصفوفة لبعض الرموز")
                result.append(cls._CAESAR_85[output_index])
        return "".join(result)

    @classmethod
    def _monoalphabetic(cls, text, *, decrypt, key, parameter):
        source, target = (cls._MONO_TO, cls._MONO_FROM) if decrypt else (
            cls._MONO_FROM,
            cls._MONO_TO,
        )
        return "".join(target[source.index(char)] if char in source else "\0" for char in text)

    @staticmethod
    def _vigenere(text, *, decrypt, key, parameter):
        if not key:
            raise LegacyCipherError("مفتاح Vigenere مطلوب")
        output = []
        key_index = 0
        for char in text.upper():
            if not "A" <= char <= "Z":
                continue
            key_char = key[key_index % len(key)]
            shift = ord(char) - ord(key_char) if decrypt else ord(char) + ord(key_char) - 2 * ord("A")
            output.append(chr(CipherService._java_remainder(shift + (26 if decrypt else 0), 26) + ord("A")))
            key_index += 1
        return "".join(output)

    @staticmethod
    def _rail_fence(text, *, decrypt, key, parameter):
        try:
            depth = int(parameter)
        except (TypeError, ValueError) as exc:
            raise LegacyCipherError("عمق Rail Fence مطلوب كعدد صحيح") from exc
        if depth <= 0:
            raise LegacyCipherError("يجب أن يكون العمق أكبر من صفر")
        columns = len(text) // depth
        if columns == 0:
            return ""
        if not decrypt:
            matrix = [["X"] * columns for _ in range(depth)]
            index = 0
            for column in range(columns):
                for row in range(depth):
                    if index < len(text):
                        matrix[row][column] = text[index]
                        index += 1
            return "".join("".join(row) for row in matrix)
        matrix = [list(text[row * columns : (row + 1) * columns]) for row in range(depth)]
        return "".join(matrix[row][column] for column in range(columns) for row in range(depth))

    @staticmethod
    def _playfair_prepare(text):
        normalized = text.replace("j", "i")
        pairs = []
        index = 0
        while index < len(normalized):
            first = normalized[index]
            if index + 1 == len(normalized):
                pairs.append(first + "x")
                index += 1
            elif normalized[index + 1] == first:
                pairs.append(first + "x")
                index += 1
            else:
                pairs.append(first + normalized[index + 1])
                index += 2
        return pairs

    @classmethod
    def _playfair(cls, text, *, decrypt, key, parameter):
        if not key:
            raise LegacyCipherError("مفتاح Playfair مطلوب")
        key_word = "".join(dict.fromkeys(key))
        alphabet = "abcdefghiklmnopqrstuvwxyz"
        table = list(dict.fromkeys(key_word + "".join(c for c in alphabet if c not in key_word)))
        if len(table) != 25:
            raise LegacyCipherError("مفتاح Playfair يجب أن يتكون من أحرف إنجليزية صغيرة")
        positions = {char: divmod(index, 5) for index, char in enumerate(table)}
        pairs = cls._playfair_prepare(text) if not decrypt else [text[i : i + 2] for i in range(0, len(text), 2)]
        if any(len(pair) != 2 for pair in pairs):
            raise LegacyCipherError("نص Playfair المشفر يجب أن يكون بطول زوجي")
        direction = -1 if decrypt else 1
        result = []
        for first, second in pairs:
            first, second = first.replace("j", "i"), second.replace("j", "i")
            if first not in positions or second not in positions:
                raise LegacyCipherError("Playfair يقبل الأحرف الإنجليزية الصغيرة فقط")
            row_a, col_a = positions[first]
            row_b, col_b = positions[second]
            if row_a == row_b:
                result.extend((table[row_a * 5 + (col_a + direction) % 5], table[row_b * 5 + (col_b + direction) % 5]))
            elif col_a == col_b:
                result.extend((table[((row_a + direction) % 5) * 5 + col_a], table[((row_b + direction) % 5) * 5 + col_b]))
            else:
                result.extend((table[row_a * 5 + col_b], table[row_b * 5 + col_a]))
        return "".join(result)

    @staticmethod
    def _matrix_from_key(key):
        size = math.isqrt(len(key))
        if not key or size * size != len(key):
            raise LegacyCipherError("طول مفتاح Hill يجب أن يكون مربعاً كاملاً")
        if any(not "a" <= char <= "z" for char in key):
            raise LegacyCipherError("مفتاح Hill يقبل الأحرف الإنجليزية الصغيرة فقط")
        return [[ord(key[row * size + col]) - 97 for col in range(size)] for row in range(size)]

    @classmethod
    def _hill(cls, text, *, decrypt, key, parameter):
        matrix = cls._matrix_from_key(key)
        size = len(matrix)
        if decrypt:
            matrix = cls._inverse_matrix_mod(matrix, 26)
        normalized = text.lower()
        if any(not "a" <= char <= "z" for char in normalized):
            raise LegacyCipherError("Hill يقبل الأحرف الإنجليزية فقط")
        normalized += "x" * ((-len(normalized)) % size)
        output = []
        for offset in range(0, len(normalized), size):
            block = [ord(char) - 97 for char in normalized[offset : offset + size]]
            output.extend(chr(sum(matrix[row][col] * block[col] for col in range(size)) % 26 + 97) for row in range(size))
        return "".join(output)

    @staticmethod
    def _determinant(matrix):
        if len(matrix) == 1:
            return matrix[0][0]
        if len(matrix) == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        return sum((-1) ** col * matrix[0][col] * CipherService._determinant(
            [row[:col] + row[col + 1 :] for row in matrix[1:]]
        ) for col in range(len(matrix)))

    @classmethod
    def _inverse_matrix_mod(cls, matrix, modulus):
        determinant = cls._determinant(matrix) % modulus
        try:
            inverse_det = pow(determinant, -1, modulus)
        except ValueError as exc:
            raise LegacyCipherError("محدد مفتاح Hill غير قابل للعكس بترديد 26") from exc
        if len(matrix) == 1:
            return [[inverse_det]]
        cofactors = []
        for row in range(len(matrix)):
            cofactor_row = []
            for col in range(len(matrix)):
                minor = [line[:col] + line[col + 1 :] for i, line in enumerate(matrix) if i != row]
                cofactor_row.append(((-1) ** (row + col) * cls._determinant(minor)) % modulus)
            cofactors.append(cofactor_row)
        return [[cofactors[col][row] * inverse_det % modulus for col in range(len(matrix))] for row in range(len(matrix))]

    @staticmethod
    def _atbash(text, *, decrypt, key, parameter):
        shift = -2 if decrypt else 2
        return "".join(chr(ord(char) + shift) for char in text)

    @staticmethod
    def _rot13(text, *, decrypt, key, parameter):
        def rotate(char):
            if "a" <= char <= "z":
                return chr((ord(char) - 97 + 13) % 26 + 97)
            if "A" <= char <= "Z":
                return chr((ord(char) - 65 + 13) % 26 + 65)
            return char

        return "".join(rotate(char) for char in text)

    @staticmethod
    def _vernam(text, *, decrypt, key, parameter):
        if not key or len(key) != len(text):
            raise LegacyCipherError("طول مفتاح Vernam يجب أن يساوي طول النص")
        result = []
        for char, pad in zip(text, key):
            value = ord(char) - 97 + (ord(pad) - 97) * (-1 if decrypt else 1)
            if not decrypt and value > 25:
                value -= 26
            if decrypt and value < 0:
                value += 26
            result.append(chr(value + 97))
        return "".join(result)

    @staticmethod
    def _java_random(seed):
        state = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

        def next_bits(bits):
            nonlocal state
            state = (state * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
            return state >> (48 - bits)

        def next_double():
            return ((next_bits(26) << 27) + next_bits(27)) / float(1 << 53)

        return next_double

    @classmethod
    def _vernam_random(cls, text, *, decrypt, key, parameter):
        if decrypt:
            raise LegacyCipherError("مصدر Java يحتوي تشفير Vernam العشوائي فقط ولا يحتوي فكاً")
        random_double = cls._java_random(7)
        output = []
        for char in text:
            if char.isalpha() and ord(char) <= 127:
                shift = int(random_double() * 26)
                output.append(chr((ord(char.upper()) - 65 + shift) % 26 + 65))
            else:
                output.append(char)
        return "".join(output)

    @classmethod
    def _otp_binary(cls, text, *, decrypt, key, parameter):
        pattern = "1010101"
        if not decrypt:
            encoded = []
            for char in text:
                bits = format(ord(char), "b")
                if len(bits) > 7:
                    raise LegacyCipherError("OneTimePad القديم يقبل محارف 7-bit فقط")
                if len(bits) != 7:
                    bits = "0" + bits
                encoded.append("".join(str(int(bit) ^ int(pattern[index])) for index, bit in enumerate(bits)))
            return " ".join(encoded) + (" " if encoded else "")
        filtered = "".join(char for char in text if char in "01 ")
        groups = filtered.split(" ")
        output = []
        for group in groups:
            if not group:
                continue
            xor_length = len(group)
            if len(group) > len(pattern):
                raise LegacyCipherError("النص لا يمكن فكّه وفق تنفيذ OneTimePad القديم")
            bits = "".join("0" if group[index] == pattern[index] else "1" for index in range(xor_length))
            output.append(chr(int(bits or "0", 2)))
        return "".join(output)

    @classmethod
    def _des(cls, text, *, decrypt, key, parameter):
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives.padding import PKCS7
            try:
                from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES

                triple_des = TripleDES
            except ImportError:
                triple_des = algorithms.TripleDES
        except ImportError as exc:
            raise LegacyCipherError("DES يتطلب حزمة cryptography") from exc
        try:
            key_bytes = bytes.fromhex(key) if len(key) == 16 else key.encode("latin-1")
        except (ValueError, UnicodeEncodeError) as exc:
            raise LegacyCipherError("مفتاح DES يجب أن يكون 8 بايت أو 16 خانة hex") from exc
        if len(key_bytes) != 8:
            raise LegacyCipherError("مفتاح DES يجب أن يكون 8 بايت بالضبط")
        try:
            payload = base64.b64decode(text, validate=True) if decrypt else text.encode("utf-8")
            cipher = Cipher(triple_des(key_bytes * 3), modes.CBC(cls._DES_IV))
            context = cipher.decryptor() if decrypt else cipher.encryptor()
            if decrypt:
                unpadder = PKCS7(64).unpadder()
                result = unpadder.update(context.update(payload) + context.finalize())
                return (result + unpadder.finalize()).decode("utf-8")
            padder = PKCS7(64).padder()
            padded = padder.update(payload) + padder.finalize()
            return base64.b64encode(context.update(padded) + context.finalize()).decode("ascii")
        except Exception as exc:
            raise LegacyCipherError("تعذر تنفيذ DES: تحقق من المفتاح أو النص المشفر") from exc

    @classmethod
    def _rsa(cls, text, *, decrypt, key, parameter):
        values = {}
        for item in (key or "").split(","):
            if "=" in item:
                name, value = item.split("=", 1)
                values[name.strip().lower()] = value.strip()
        try:
            exponent = int(values["d" if decrypt else "e"], 0)
            modulus = int(values["n"], 0)
            if decrypt:
                message = base64.b64decode(text, validate=True)
                number = int.from_bytes(message, "big", signed=True)
            else:
                number = int.from_bytes(text.encode("utf-8"), "big", signed=True)
            result = pow(number, exponent, modulus)
            if result == 0:
                encoded = b"\0"
            else:
                length = (result.bit_length() + 8) // 8
                encoded = result.to_bytes(length, "big", signed=True)
            if decrypt:
                return encoded.decode("utf-8")
            return base64.b64encode(encoded).decode("ascii")
        except (KeyError, ValueError, OverflowError) as exc:
            raise LegacyCipherError("RSA يحتاج e/d و n صحيحين، ورسالة أصغر من n") from exc

    @staticmethod
    def _dsa(text, *, decrypt, key, parameter):
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import dsa
            from cryptography.hazmat.primitives.serialization import load_der_private_key, load_der_public_key

            key_bytes = base64.b64decode(key, validate=True)
            payload = text.encode("utf-8")
            if decrypt:
                public_key = load_der_public_key(key_bytes)
                signature = base64.b64decode(parameter, validate=True)
                public_key.verify(signature, payload, hashes.SHA1())
                return "true"
            private_key = load_der_private_key(key_bytes, password=None)
            signature = private_key.sign(payload, hashes.SHA1())
            return base64.b64encode(signature).decode("ascii")
        except ImportError as exc:
            raise LegacyCipherError("DSA يتطلب حزمة cryptography") from exc
        except Exception as exc:
            raise LegacyCipherError("تعذر توقيع البيانات أو التحقق من توقيع DSA") from exc

    @staticmethod
    def _xor_shares(text, *, decrypt, key, parameter):
        if not decrypt:
            try:
                count = int(parameter or 2)
            except (TypeError, ValueError) as exc:
                raise LegacyCipherError("عدد حصص XOR غير صالح") from exc
            if count < 2:
                raise LegacyCipherError("يلزم حصتان على الأقل")
            encoded = text.encode("latin-1", errors="strict")
            shares = [bytes(secrets.token_bytes(len(encoded))) for _ in range(count - 1)]
            last = bytearray(encoded)
            for share in shares:
                for index, value in enumerate(share):
                    last[index] ^= value
            shares.append(bytes(last))
            return "\n".join(base64.b64encode(share).decode("ascii") for share in shares)
        try:
            shares = [base64.b64decode(line, validate=True) for line in text.splitlines() if line.strip()]
        except ValueError as exc:
            raise LegacyCipherError("كل حصة XOR يجب أن تكون Base64 صحيحة") from exc
        if len(shares) < 2 or len({len(share) for share in shares}) != 1:
            raise LegacyCipherError("يلزم حصتان متساويتان في الطول")
        result = bytearray(shares[0])
        for share in shares[1:]:
            for index, value in enumerate(share):
                result[index] ^= value
        return bytes(result).decode("latin-1")
# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import base64
import hashlib

from tbears.libs.icx_signer import IcxSigner, key_from_key_store
from secp256k1 import PrivateKey
from tbears.tbears_exception import KeyStoreException


class TestIcxSigner(unittest.TestCase):
    def setUp(self):
        self.test_private_key = PrivateKey()
        self.signer = IcxSigner(self.test_private_key.private_key)

        m = hashlib.sha256()
        m.update(b'message_for_test')
        # prepare massage msg_hash
        self.hashed_message = m.digest()

        # check if signature which sign_recoverable method made is valid
        # use ecdsa_verify. before verify signature, convert sign (recoverable_sig -> normal_sig)
        # check secp256k1 doc: https://github.com/ludbb/secp256k1-py

    def test_sign_recoverable_verify_sig(self):
        # get sign, recovery
        sign, recovery_id = self.signer.sign_recoverable(self.hashed_message)

        # Convert recoverable sig to normal sig
        deserialized_recoverable_sig = self.test_private_key.ecdsa_recoverable_deserialize(sign, recovery_id)
        normal_sig = self.test_private_key.ecdsa_recoverable_convert(deserialized_recoverable_sig)

        # Check sig
        self.assertTrue(self.test_private_key.pubkey.ecdsa_verify(self.hashed_message, normal_sig, raw=True))

        # Verify using invalid message
        m = hashlib.sha256()
        m.update(b'invalid message')
        invalid_message = m.digest()
        self.assertFalse(self.test_private_key.pubkey.ecdsa_verify(invalid_message, normal_sig, raw=True))

        # Verify using invalid private key
        invalid_privateKey = PrivateKey()
        self.assertFalse(invalid_privateKey.pubkey.ecdsa_verify(self.hashed_message, normal_sig, raw=True))

    def test_sign_base64_encode(self):
        # make signature
        encoded_sign = self.signer.sign(self.hashed_message)
        decoded_sign = base64.b64decode(encoded_sign)

        actual_id = int.from_bytes(decoded_sign[-1:], byteorder='big')
        actual_sig = decoded_sign[:len(decoded_sign) - 1]

        expected_signature, expected_recovery_id = self.signer.sign_recoverable(self.hashed_message)
        self.assertEqual(actual_id, expected_recovery_id)
        self.assertEqual(actual_sig, expected_signature)

    def test_key_from_key_store_get_private_key(self):
        # Invalid keystore file path
        self.assertRaises(KeyStoreException, key_from_key_store, './invalid_file_path', 'qwer1234%')

        # Invalid keystore password
        self.assertRaises(KeyStoreException, key_from_key_store, './tests/test_util/test_keystore', 'qwer12')










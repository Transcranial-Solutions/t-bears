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
import shutil
import unittest
import os
import socket

from iconcommons.icon_config import IconConfig

from tbears.command.command import Command
from tbears.libs.icon_jsonrpc import IconClient
from tbears.config.tbears_config import tbears_server_config
from tbears.tbears_exception import IconClientException
from tests.test_util import TEST_UTIL_DIRECTORY


class TestIconClient(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        tbears_server_config_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_server_config.json')
        self.conf = IconConfig(tbears_server_config_path, tbears_server_config)
        self.conf.load()
        self.conf['config'] = tbears_server_config_path
        self.cmd.cmdServer.start(self.conf)

        # Check server started (before test Icon client, sever has to be started)
        self.assertTrue(self.check_server())

    def check_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result = sock.connect_ex(('127.0.0.1', 9000))
        sock.close()
        return result == 0

    def tearDown(self):
        if self.check_server():
            self.cmd.cmdServer.stop(self.conf)
        if os.path.exists('exc'):
            shutil.rmtree('exc')
        if os.path.exists('tbears.log'):
            os.remove('tbears.log')

    def test_send_request_to_server(self):
        # Correct request
        payload = {"jsonrpc": "2.0", "method": "icx_getTotalSupply", "id": 111}
        client = IconClient('http://127.0.0.1:9000/api/v3')
        response = client.send(payload)

        # the return type should 'dict'
        expected_type = type({})
        self.assertEqual(type(response), expected_type)

        self.assertIsNotNone(response['result'])

        # Incorrect request: input url which is omitted port number
        payload = {"jsonrpc": "2.0", "method": "icx_getTotalSupply", "id": 111}
        client = IconClient('http://127.0.0.1:/api/v3')
        # check get response correctly, don't check the response data
        self.assertRaises(Exception, client.send, payload)

        # Incorrect request: invalid url to working server
        payload = {"jsonrpc": "2.0", "method": "icx_getTotalSupply", "id": 111}
        client = IconClient('http://127.0.0.1:9000/api/invalidUrl')
        # check get response correctly, don't check the response data
        self.assertRaises(IconClientException, client.send, payload)

        # Incorrect request: invalid url to not working service
        payload = {"jsonrpc": "2.0", "method": "icx_getTotalSupply", "id": 111}
        client = IconClient('http://127.0.0.1:19001/api/invalidUrl')
        # check get response correctly, don't check the response data
        self.assertRaises(Exception, client.send, payload)

        # Bad request: invalid payload data (nonexistent method name)
        incorrect_payload = {"jsonrpc": "2.0", "method": "icx_invalid_requests", "id": 111}
        client = IconClient('http://127.0.0.1:9000/api/v3')
        response = client.send(incorrect_payload)
        self.assertIsNotNone(response['error'])

        # Bad request: insufficient payload data (method is not set)
        insufficient_payload = {"jsonrpc": "2.0", "id": 111}
        client = IconClient('http://127.0.0.1:9000/api/v3')
        response = client.send(insufficient_payload)
        self.assertIsNotNone(response['error'])

        # requests when server stopped
        self.cmd.cmdServer.stop(self.conf)
        payload = {"jsonrpc": "2.0", "method": "icx_getTotalSupply", "id": 111}
        client = IconClient('http://127.0.0.1:9000/api/v3')
        self.assertRaises(Exception, client.send, payload)

        self.cmd.cmdScore.clear(self.conf)

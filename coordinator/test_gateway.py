import unittest
import requests

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.url = 'http://localhost:12342'
        self.password = "Fuckyou"

    def test_login_success(self):
        endpoint = "/verification"
        response = requests.post(self.url + endpoint, json={'password': self.password})
        self.assertEqual(response.status_code, 200)
        session_key = response.json()['sessionKey']
        # Set the session_key into cookie
        self.session_key = session_key

    def test_login_failure(self):
        endpoint = "/verification"
        response = requests.post(self.url + endpoint, json={'password': "random password"})
        self.assertEqual(response.status_code, 400)

    def test_get_clash_file(self):
        self.test_login_success()
        endpoint = "/clash_file"
        response = requests.get(self.url + endpoint, cookies={'session_key': self.session_key})
        self.assertEqual(response.status_code, 200)

    def test_get_relay_list(self):
        self.test_login_success()
        endpoint = "/relay_list"
        response = requests.get(self.url + endpoint, cookies={'session_key': self.session_key})
        self.assertEqual(response.status_code, 200)

    def test_put_relay_node(self):
        self.test_login_success()
        endpoint = "/update_node"
        virtual_node = {"ip": "1.4.3.1", "node_id": "test-1", "port": 1234}
        self.virtual_nodes = {}
        virtual_nodes = []
        for i in range(10):
            new_virtual_node = virtual_node.copy()
            new_virtual_node['node_id'] = "test-" + str(i)
            virtual_nodes.append(new_virtual_node)
            response = requests.post(self.url + endpoint, json=new_virtual_node, cookies={'session_key': self.session_key})
            self.assertEqual(response.status_code, 200)
            self.virtual_nodes[new_virtual_node['node_id']] = {"ip": new_virtual_node['ip'], "port": new_virtual_node['port']}


    def test_get_relay_node(self):

        self.test_put_relay_node()

        self.test_login_success()
        endpoint = "/relay_list"
        response = requests.get(self.url + endpoint, cookies={'session_key': self.session_key})
        self.assertEqual(response.status_code, 200)

        get_nodes = response.json()['relay_list']

        # Remove the last_seen field
        for node in get_nodes:
            get_nodes[node].pop('last_seen', None)

        get_nodes.pop('aaa', None)

        for node in get_nodes:
            self.assertTrue(node in list(self.virtual_nodes.keys()))

    def test_timeout_nodes(self):
        self.test_put_relay_node()
        self.test_login_success()
        endpoint = "/relay_list"
        response = requests.get(self.url + endpoint, cookies={'session_key': self.session_key})
        self.assertEqual(response.status_code, 200)

        get_nodes = response.json()['relay_list']
        self.assertEqual(len(get_nodes), 10 )

        # Wait for 10 seconds
        import time
        print("Waiting for 10 seconds")
        time.sleep(10)
        response = requests.get(self.url + endpoint, cookies={'session_key': self.session_key})
        self.assertEqual(response.status_code, 200)
        get_nodes = response.json()['relay_list']
        self.assertEqual(len(get_nodes), 0)




if __name__ == '__main__':
    unittest.main()

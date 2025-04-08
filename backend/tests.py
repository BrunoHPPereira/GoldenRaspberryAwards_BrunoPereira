import unittest
import json
import os
import tempfile
from backend.app import app, init_db, load_csv_data


class APITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        # Create a temp CSV file with test data
        self.csv_fd, self.csv_path = tempfile.mkstemp()
        with os.fdopen(self.csv_fd, 'w') as f:
            f.write('''year;title;studios;producers;winner
1980;Test Movie 1;Studio A;John Producer;yes
1981;Test Movie 2;Studio B;Jane Producer;
1990;Test Movie 3;Studio C;John Producer;yes
1991;Test Movie 4;Studio D;Jane Producer;yes
2000;Test Movie 5;Studio E;John Producer;yes
2001;Test Movie 6;Studio F;Jane Producer;yes
2002;Test Movie 7;Studio G;Quick Producer;yes
2003;Test Movie 8;Studio H;Quick Producer;yes
''')

        # Initialize test database
        self.db_connection = init_db()
        load_csv_data(self.db_connection, self.csv_path)

    def tearDown(self):
        os.unlink(self.csv_path)

    def test_producer_intervals(self):
        response = self.app.get('/api/producers/awards-interval')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        # Test structure
        self.assertIn('min', data)
        self.assertIn('max', data)

        # Test min interval
        self.assertEqual(len(data['min']), 1)
        self.assertEqual(data['min'][0]['producer'], 'Quick Producer')
        self.assertEqual(data['min'][0]['interval'], 1)
        self.assertEqual(data['min'][0]['previousWin'], 2002)
        self.assertEqual(data['min'][0]['followingWin'], 2003)

        # Test max interval
        self.assertEqual(len(data['max']), 1)
        self.assertEqual(data['max'][0]['producer'], 'John Producer')
        self.assertEqual(data['max'][0]['interval'], 10)
        self.assertEqual(data['max'][0]['previousWin'], 1990)
        self.assertEqual(data['max'][0]['followingWin'], 2000)

    def test_response_format(self):
        response = self.app.get('/api/producers/awards-interval')
        data = json.loads(response.data)

        # Verify structure of response matches the specified format
        for interval_type in ['min', 'max']:
            self.assertIsInstance(data[interval_type], list)

            for item in data[interval_type]:
                self.assertIsInstance(item, dict)
                self.assertIn('producer', item)
                self.assertIn('interval', item)
                self.assertIn('previousWin', item)
                self.assertIn('followingWin', item)

                self.assertIsInstance(item['producer'], str)
                self.assertIsInstance(item['interval'], int)
                self.assertIsInstance(item['previousWin'], int)
                self.assertIsInstance(item['followingWin'], int)


if __name__ == '__main__':
    unittest.main()
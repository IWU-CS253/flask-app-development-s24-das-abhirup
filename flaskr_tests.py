import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):


    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])


    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data


    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'A category' in rv.data


    def test_filter_entries_all(self):
        # Test when filter_category is "all"
        response = self.app.get('/filter_entries?category=all')
        self.assertEqual(response.status_code, 200)


    def test_filter_entries_specific_category(self):
        response = self.app.get('/filter_entries?category=some_category')
        self.assertEqual(response.status_code, 200)


    def test_delete_entry(self):
        # Create a test entry in the database to delete
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('INSERT INTO entries (id, title, text, category) VALUES (?, ?, ?, ?)', [1, 'data1', 'data2', 'data3'])
            db.commit()

        # Send a POST request to delete the test entry
        response = self.app.post('/delete', data={'id': 1})
        self.assertEqual(response.status_code, 302)

        # Check if the test entry was deleted from the database
        with flaskr.app.app_context():
            db = flaskr.get_db()
            entry = db.execute('SELECT * FROM entries WHERE id = ?', [1]).fetchone()
            self.assertIsNone(entry)


    def test_show_entries_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)


    def test_update_entry(self):
        mock_data = {
            'title': 'Updated Title',
            'category': 'Updated Category',
            'text': 'Updated Text',
            'id': 1
        }

        response = self.app.post('/update', data=mock_data)
        self.assertEqual(response.status_code, 302)
        with self.app.session_transaction() as session:
            flash_message = dict(session['_flashes']).get('info')
            self.assertEqual(flash_message, 'Entry was successfully updated')


    def test_update_redirect(self):
        test_id = 123
        response = self.app.get(f'/update-redirect?id={test_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(str(test_id), 'utf-8'), response.data)


if __name__ == '__main__':
    unittest.main()

from unittest import TestCase
from app import create_app, db
from app.models import Member


class TestMemberRoutes(TestCase):
    def setUp(self):
        """Set up the test client and app context."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_hello_world(self):
        """Test the hello world route."""
        response = self.client.get('/api/books/hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello world')

    def test_create(self):
        """Check create endpoint creates a new member."""
        member_data = {
            "name": 'Jane Doe',
            "debt": 0
        }
        
        response = self.client.post('/api/members/create', json=member_data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Jane Doe', response.json['Member']['name'])
        self.assertEqual(0, response.json['Member']['debt'])
        self.assertEqual(0, response.json['Member']['books_borrowed'])

    def test_create_on_invalid_data(self):
        """Check if create endpoint returns error on invalid data."""
        member_data = {
            "name": 'Jane Doe',
            "debt": None
        }
        
        response = self.client.post('/api/members/create', json=member_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Validation failed', response.json['Error'])

    def test_update(self):
        """Check update endpoint updates a member."""
        member = Member(name='Jane Doe', debt=0)
        db.session.add(member)
        db.session.commit()
        
        member_data = {
            "name": 'Jane Doe',
            "debt": 100
        }
        
        response = self.client.put(f'/api/members/update/{member.id}', json=member_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Jane Doe', response.json['Member']['name'])
        self.assertEqual(100, response.json['Member']['debt'])

    def test_update_on_invalid_data(self):
        """Check if update endpoint returns error on invalid data."""
        member = Member(name='Jane Doe', debt=0)
        db.session.add(member)
        db.session.commit()
        
        member_data = {
            "name": 'Jane Doe',
            "debt": None
        }
        
        response = self.client.put(f'/api/members/update/{member.id}', json=member_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Validation failed', response.json['Error'])

    def test_get_member_by_id(self):
        """Check if get member by id endpoint returns a member."""
        member = Member(name='Jane Doe', debt=0)
        db.session.add(member)
        db.session.commit() 
        
        retrieved_member = Member.query.filter_by(name='Jane Doe').first()
        
        response = self.client.get(f'/api/members/get_by_id/{retrieved_member.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Jane Doe', response.json['name'])
        self.assertEqual(0, response.json['debt'])

    def test_get_member_by_id_on_invalid_id(self):
        """Check if get member by id endpoint returns error on invalid id."""
        response = self.client.get('/api/members/get_by_id/100')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Could not find member!', response.json['Error'])

    def test_get_all_members(self):
        """Check if get all members endpoint returns all members."""
        member1 = Member(name='Jane Doe', debt=0)
        member2 = Member(name='John Doe', debt=0)
        member3 = Member(name='Janet White', debt=0)
        member4 = Member(name='John White', debt=0)
        member5 = Member(name='Peaches Freeman', debt=0)
        
        db.session.add_all([member1, member2, member3, member4, member5])
        db.session.commit() 
        
        payload = {
            'page': 1,
            'per_page': 2
        }
        
        response = self.client.get('/api/members/get_members', query_string=payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, response.json['total_pages'])
        self.assertEqual(2, len(response.json['members']))
        self.assertEqual(5, response.json['total_members'])
        self.assertEqual(3, response.json['pages'])
        self.assertEqual(1, response.json['current_page'])
        self.assertEqual(True, response.json['has_next'])
        self.assertEqual(False, response.json['has_prev'])
        self.assertEqual(2, response.json['next_page'])
        self.assertEqual(None, response.json['prev_page'])

    def test_delete_member(self):
        """Check if delete member endpoint deletes a member."""
        member = Member(name='Jane Doe', debt=0)
        db.session.add(member)
        db.session.commit()
        
        response = self.client.delete(f'/api/members/delete/{member.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Member deleted succesfully!', response.json['Message'])

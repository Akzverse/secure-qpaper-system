#!/usr/bin/env python3
"""Initialize demo users for testing the system"""

from app import app, db, User, init_db
from werkzeug.security import generate_password_hash

def create_demo_users():
    """Create demo users for testing all roles"""
    with app.app_context():
        # Initialize database
        init_db()
        
        # Demo users to create
        demo_users = [
            {
                'username': 'qs1',
                'email': 'questionsetter@example.com',
                'password': 'password123',
                'role': 'question_setter'
            },
            {
                'username': 'qs2',
                'email': 'questionsetter2@example.com',
                'password': 'password123',
                'role': 'question_setter'
            },
            {
                'username': 'reviewer1',
                'email': 'reviewer@example.com',
                'password': 'password123',
                'role': 'reviewer'
            },
            {
                'username': 'officer1',
                'email': 'officer@example.com',
                'password': 'password123',
                'role': 'exam_officer'
            },
            {
                'username': 'officer2',
                'email': 'officer2@example.com',
                'password': 'password123',
                'role': 'exam_officer'
            }
        ]
        
        for user_data in demo_users:
            # Check if user already exists
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=generate_password_hash(user_data['password']),
                    role=user_data['role']
                )
                db.session.add(user)
                print(f"[OK] Created user: {user_data['username']} ({user_data['role']})")
            else:
                print(f"[INFO] User already exists: {user_data['username']}")
        
        db.session.commit()
        print("\nDatabase initialized successfully!")
        print("\nDemo Users Created:")
        print("-" * 50)
        print("Admin:            admin / admin@123")
        print("Question Setter:  qs1 / password123")
        print("Question Setter:  qs2 / password123")
        print("Reviewer:         reviewer1 / password123")
        print("Exam Officer:     officer1 / password123")
        print("Exam Officer:     officer2 / password123")
        print("-" * 50)

if __name__ == '__main__':
    create_demo_users()

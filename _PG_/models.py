from database import db, Room, Tenant, Payment, Complaint, Enquiry
from datetime import datetime, date

def init_db():
    """Initialize database with sample data"""
    # Add sample rooms
    rooms = [
        Room(room_number='101', floor='Ground', room_type='Single', sharing_type='1', 
             rent_amount=8000, security_deposit=16000, status='Available'),
        Room(room_number='102', floor='Ground', room_type='Sharing', sharing_type='2', 
             rent_amount=5000, security_deposit=10000, status='Available'),
        Room(room_number='201', floor='First', room_type='Single', sharing_type='1', 
             rent_amount=9000, security_deposit=18000, status='Occupied'),
        Room(room_number='202', floor='First', room_type='Sharing', sharing_type='3', 
             rent_amount=4000, security_deposit=8000, status='Maintenance'),
    ]
    
    for room in rooms:
        if not Room.query.filter_by(room_number=room.room_number).first():
            db.session.add(room)
    
    # Add sample tenant
    if not Tenant.query.first():
        sample_tenant = Tenant(
            full_name="Aman Sharma",
            gender="Male",
            date_of_birth=date(1990, 5, 15),
            phone_number="9876543210",
            email="aman@example.com",
            aadhaar_number="123456789012",
            emergency_contact="9876543211",
            address_line1="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            pin_code="400001",
            room_id=3,  # Room 201
            move_in_date=date(2024, 1, 1),
            agreement_period=11,
            monthly_rent=9000,
            security_deposit_paid=18000
        )
        db.session.add(sample_tenant)
    
    db.session.commit()
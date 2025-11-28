from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    floor = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    sharing_type = db.Column(db.String(20), nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, nullable=False)
    facilities = db.Column(db.Text)
    room_features = db.Column(db.Text)
    status = db.Column(db.String(20), default='Available')
    availability_date = db.Column(db.Date)
    additional_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    aadhaar_number = db.Column(db.String(12), nullable=False)
    pan_number = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(15), nullable=False)
    address_line1 = db.Column(db.Text, nullable=False)
    address_line2 = db.Column(db.Text)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    
    # Room allocation
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref('tenants', lazy=True))
    bed_number = db.Column(db.String(10))
    move_in_date = db.Column(db.Date, nullable=False)
    agreement_period = db.Column(db.Integer, nullable=False)  # in months
    rent_due_date = db.Column(db.Integer, default=5)  # day of month
    monthly_rent = db.Column(db.Float, nullable=False)
    security_deposit_paid = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    tenant = db.relationship('Tenant', backref=db.backref('payments', lazy=True))
    payment_type = db.Column(db.String(50), nullable=False)
    payment_for = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    reference_number = db.Column(db.String(100))
    received_by = db.Column(db.String(100), default='Admin')
    additional_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    tenant = db.relationship('Tenant', backref=db.backref('complaints', lazy=True))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship('Room', backref=db.backref('complaints', lazy=True))
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    assigned_to = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Open')
    photos = db.Column(db.Text)  # JSON string of photo paths
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    enquiry_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='New')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
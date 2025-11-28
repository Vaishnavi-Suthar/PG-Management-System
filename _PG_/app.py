from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database import db, Room, Tenant, Payment, Complaint, Enquiry
from models import init_db
from datetime import datetime, date, timedelta
import json
import csv
from io import StringIO
from flask import Response


app = Flask(__name__)
app.config['SECRET_KEY'] = 'adccd3ddff4727d42820b153a39e0113'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pg_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# ✅ Add this line right after app creation
app.jinja_env.globals['now'] = datetime.now

# Admin credentials (in production, use proper authentication)
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

with app.app_context():
    db.create_all()
    init_db()

# Login required decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

import csv
from io import StringIO, BytesIO
from flask import Response
from datetime import datetime

# Export Routes -------------------------

@app.route('/export_tenants')
@login_required
def export_tenants():
    try:
        tenants = Tenant.query.all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Full Name', 'Gender', 'Phone', 'Email', 'Aadhaar', 
                        'Room Number', 'Bed Number', 'Move-in Date', 'Monthly Rent', 
                        'Status', 'Emergency Contact'])
        
        # Write data
        for tenant in tenants:
            writer.writerow([
                tenant.id,
                tenant.full_name,
                tenant.gender,
                tenant.phone_number,
                tenant.email or '',
                tenant.aadhaar_number,
                tenant.room.room_number if tenant.room else 'N/A',
                tenant.bed_number or '',
                tenant.move_in_date.strftime('%Y-%m-%d') if tenant.move_in_date else '',
                tenant.monthly_rent,
                tenant.status,
                tenant.emergency_contact
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=tenants_export.csv",
                "Content-type": "text/csv; charset=utf-8"
            }
        )
        
    except Exception as e:
        flash(f'Error exporting tenants: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/export_payments')
@login_required
def export_payments():
    try:
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Tenant Name', 'Payment Type', 'Payment For', 
                        'Amount', 'Payment Date', 'Payment Method', 'Reference Number',
                        'Received By', 'Created At'])
        
        # Write data
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.tenant.full_name,
                payment.payment_type,
                payment.payment_for,
                payment.amount,
                payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else '',
                payment.payment_method,
                payment.reference_number or '',
                payment.received_by,
                payment.created_at.strftime('%Y-%m-%d %H:%M') if payment.created_at else ''
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=payments_export.csv",
                "Content-type": "text/csv; charset=utf-8"
            }
        )
        
    except Exception as e:
        flash(f'Error exporting payments: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/export_rooms')
@login_required
def export_rooms():
    try:
        rooms = Room.query.all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Room Number', 'Floor', 'Room Type', 'Sharing Type',
                        'Rent Amount', 'Security Deposit', 'Status', 'Facilities',
                        'Availability Date', 'Current Tenants'])
        
        # Write data
        for room in rooms:
            current_tenants = len([t for t in room.tenants if t.status == 'Active'])
            writer.writerow([
                room.id,
                room.room_number,
                room.floor,
                room.room_type,
                room.sharing_type,
                room.rent_amount,
                room.security_deposit,
                room.status,
                room.facilities or '',
                room.availability_date.strftime('%Y-%m-%d') if room.availability_date else '',
                current_tenants
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=rooms_export.csv",
                "Content-type": "text/csv; charset=utf-8"
            }
        )
        
    except Exception as e:
        flash(f'Error exporting rooms: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# PDF Export Routes -------------------------

@app.route('/export_tenants_pdf')
@login_required
def export_tenants_pdf():
    try:
        # Import reportlab here to avoid issues if not installed
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        tenants = Tenant.query.all()
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Content container
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Center aligned
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph("TENANTS REPORT", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Prepare data for table
        data = [['ID', 'Name', 'Phone', 'Room', 'Rent', 'Status', 'Move-in Date']]
        
        for tenant in tenants:
            data.append([
                str(tenant.id),
                tenant.full_name,
                tenant.phone_number,
                tenant.room.room_number if tenant.room else 'N/A',
                f"₹{tenant.monthly_rent:.2f}",
                tenant.status,
                tenant.move_in_date.strftime('%d/%m/%Y') if tenant.move_in_date else 'N/A'
            ])
        
        # Create table
        table = Table(data, colWidths=[0.5*inch, 1.5*inch, 1.2*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total Tenants: {len(tenants)}", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=tenants_report.pdf",
                "Content-type": "application/pdf"
            }
        )
        
    except ImportError:
        flash('PDF export requires ReportLab library. Please install it using: pip install reportlab', 'error')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/export_payments_pdf')
@login_required
def export_payments_pdf():
    try:
        # Import reportlab here to avoid issues if not installed
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Content container
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph("PAYMENTS REPORT", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Calculate totals
        total_amount = sum(p.amount for p in payments)
        
        # Prepare data for table
        data = [['ID', 'Tenant', 'Type', 'Period', 'Amount', 'Date', 'Method']]
        
        for payment in payments:
            data.append([
                str(payment.id),
                payment.tenant.full_name[:15] + '...' if len(payment.tenant.full_name) > 15 else payment.tenant.full_name,
                payment.payment_type,
                payment.payment_for[:10] + '...' if len(payment.payment_for) > 10 else payment.payment_for,
                f"₹{payment.amount:.2f}",
                payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else 'N/A',
                payment.payment_method
            ])
        
        # Create table
        table = Table(data, colWidths=[0.5*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total Payments: {len(payments)}", styles['Normal']))
        elements.append(Paragraph(f"Total Amount: ₹{total_amount:.2f}", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=payments_report.pdf",
                "Content-type": "application/pdf"
            }
        )
        
    except ImportError:
        flash('PDF export requires ReportLab library. Please install it using: pip install reportlab', 'error')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/export_monthly_report_pdf')
@login_required
def export_monthly_report_pdf():
    try:
        # Import reportlab here to avoid issues if not installed
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        # Get data for monthly report
        current_month = datetime.now().strftime('%B %Y')
        tenants = Tenant.query.filter_by(status='Active').all()
        payments = Payment.query.filter_by(payment_for=current_month).all()
        rooms = Room.query.all()
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph("MONTHLY MANAGEMENT REPORT", title_style))
        elements.append(Paragraph(f"Period: {current_month}", styles['Heading2']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 30))
        
        # Summary Statistics
        elements.append(Paragraph("SUMMARY STATISTICS", styles['Heading2']))
        
        total_rooms = len(rooms)
        occupied_rooms = len([r for r in rooms if r.status == 'Occupied'])
        vacant_rooms = len([r for r in rooms if r.status == 'Available'])
        total_tenants = len(tenants)
        total_collected = sum(p.amount for p in payments)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Rooms', str(total_rooms)],
            ['Occupied Rooms', str(occupied_rooms)],
            ['Vacant Rooms', str(vacant_rooms)],
            ['Active Tenants', str(total_tenants)],
            ['Monthly Collection', f"₹{total_collected:.2f}"],
            ['Occupancy Rate', f"{(occupied_rooms/total_rooms*100):.1f}%" if total_rooms > 0 else "0%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Recent Payments
        elements.append(Paragraph("RECENT PAYMENTS", styles['Heading2']))
        if payments:
            payment_data = [['Tenant', 'Amount', 'Date', 'Method']]
            for payment in payments[:10]:  # Show last 10 payments
                payment_data.append([
                    payment.tenant.full_name,
                    f"₹{payment.amount:.2f}",
                    payment.payment_date.strftime('%d/%m/%Y'),
                    payment.payment_method
                ])
            
            payment_table = Table(payment_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(payment_table)
        else:
            elements.append(Paragraph("No payments recorded this month.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("--- End of Report ---", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=monthly_report_{datetime.now().strftime('%Y_%m')}.pdf",
                "Content-type": "application/pdf"
            }
        )
        
    except ImportError:
        flash('PDF export requires ReportLab library. Please install it using: pip install reportlab', 'error')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error generating monthly report: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Helper functions
def get_dashboard_stats():
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status='Occupied').count()
    vacant_rooms = Room.query.filter_by(status='Available').count()
    total_tenants = Tenant.query.filter_by(status='Active').count()
    
    # Calculate pending rent
    current_month = datetime.now().strftime('%B %Y')
    total_pending = 0
    tenants = Tenant.query.filter_by(status='Active').all()
    for tenant in tenants:
        paid_this_month = Payment.query.filter_by(
            tenant_id=tenant.id, 
            payment_for=current_month,
            payment_type='Rent'
        ).first()
        if not paid_this_month:
            total_pending += tenant.monthly_rent
    
    # Get recent enquiries
    recent_enquiries = Enquiry.query.filter_by(status='New').count()
    
    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'total_tenants': total_tenants,
        'pending_rent': total_pending,
        'recent_enquiries': recent_enquiries
    }


# Routes
@app.route('/')
def home():
    # If already logged in, redirect to dashboard
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: {username}")  # Debug print
        
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            print("Login successful, redirecting to dashboard")  # Debug print
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials! Please try again.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        print(f"Login error: {e}")  # Debug print
        flash('An error occurred during login.', 'error')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


# Dashboard -------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    
    # Recent activities (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    
    # Get all activities and combine them
    recent_payments = Payment.query.filter(
        Payment.created_at >= yesterday
    ).order_by(Payment.created_at.desc()).limit(10).all()
    
    recent_complaints = Complaint.query.filter(
        Complaint.created_at >= yesterday
    ).order_by(Complaint.created_at.desc()).limit(10).all()
    
    recent_enquiries = Enquiry.query.filter(
        Enquiry.created_at >= yesterday
    ).order_by(Enquiry.created_at.desc()).limit(5).all()
    
    # New tenant registrations (last 24 hours)
    new_tenants = Tenant.query.filter(
        Tenant.created_at >= yesterday
    ).order_by(Tenant.created_at.desc()).limit(5).all()
    
    # Combine all activities into one list with timestamps
    all_activities = []
    
    # Add payments with type identifier
    for payment in recent_payments:
        all_activities.append({
            'type': 'payment',
            'data': payment,
            'timestamp': payment.created_at
        })
    
    # Add complaints with type identifier
    for complaint in recent_complaints:
        all_activities.append({
            'type': 'complaint',
            'data': complaint,
            'timestamp': complaint.created_at
        })
    
    # Add new tenants with type identifier
    for tenant in new_tenants:
        all_activities.append({
            'type': 'new_tenant',
            'data': tenant,
            'timestamp': tenant.created_at
        })
    
    # Add enquiries with type identifier
    for enquiry in recent_enquiries:
        all_activities.append({
            'type': 'enquiry',
            'data': enquiry,
            'timestamp': enquiry.created_at
        })
    
    # Sort all activities by timestamp (newest first)
    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Limit to 15 most recent activities
    recent_activities = all_activities[:15]
    
    # Upcoming vacancies
    upcoming_vacancies = Tenant.query.filter(
        Tenant.move_in_date <= date.today() + timedelta(days=30)
    ).all()
    
    # Pending rent defaulters
    current_month = datetime.now().strftime('%B %Y')
    defaulters = []
    for tenant in Tenant.query.filter_by(status='Active').all():
        paid = Payment.query.filter_by(
            tenant_id=tenant.id,
            payment_for=current_month,
            payment_type='Rent'
        ).first()
        if not paid:
            defaulters.append(tenant)
    
    # Count new activities for notification
    new_activities_count = len(recent_activities)
    
    return render_template('dashboard.html', 
                         stats=stats,
                         recent_activities=recent_activities,
                         upcoming_vacancies=upcoming_vacancies,
                         defaulters=defaulters,
                         new_activities_count=new_activities_count,
                         yesterday=yesterday)




# Rooms -------------------------
@app.route('/rooms')
@login_required
def rooms():
    rooms_list = Room.query.order_by(Room.room_number).all()
    stats = get_dashboard_stats()
    return render_template('add_room.html', rooms=rooms_list, stats=stats)

@app.route('/add_room', methods=['POST'])
@login_required
def add_room():
    try:
        # --- Safely get form values ---
        room_number = request.form.get('room_number', '').strip()
        floor = request.form.get('floor', '').strip()
        room_type = request.form.get('room_type', '').strip()
        sharing_type = request.form.get('sharing_type', '').strip()
        rent_amount = request.form.get('rent_amount')
        security_deposit = request.form.get('security_deposit')

        if not (room_number and floor and room_type and sharing_type and rent_amount and security_deposit):
            flash("All required fields must be filled!", "error")
            return redirect(url_for('rooms'))

        # Convert to numeric values safely
        rent_amount = float(rent_amount)
        security_deposit = float(security_deposit)

        # Get checkbox lists (these can be empty)
        facilities_list = request.form.getlist('facilities')
        room_features_list = request.form.getlist('room_features')

        # Parse optional date
        availability_date_str = request.form.get('availability_date')
        availability_date = None
        if availability_date_str:
            try:
                availability_date = datetime.strptime(availability_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format for availability date!", "error")
                return redirect(url_for('rooms'))

        # --- Create room object ---
        room = Room(
            room_number=room_number,
            floor=floor,
            room_type=room_type,
            sharing_type=sharing_type,
            rent_amount=rent_amount,
            security_deposit=security_deposit,
            facilities=", ".join(facilities_list),
            room_features=", ".join(room_features_list),
            status=request.form.get('status', 'Available'),
            availability_date=availability_date,
            additional_notes=request.form.get('additional_notes', '')
        )

        # --- Save to DB ---
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error adding room: {str(e)}', 'danger')

    return redirect(url_for('rooms'))

# Add route to get room details
# Update the existing route to include tenant information
@app.route('/api/room/<int:room_id>')
@login_required
def get_room_details(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Get all tenants in this room
        tenants = Tenant.query.filter_by(room_id=room_id, status='Active').all()
        
        # Prepare tenant information
        tenant_info = []
        for tenant in tenants:
            tenant_info.append({
                'id': tenant.id,
                'full_name': tenant.full_name,
                'phone_number': tenant.phone_number,
                'move_in_date': tenant.move_in_date.strftime('%Y-%m-%d') if tenant.move_in_date else '',
                'bed_number': tenant.bed_number
            })
        
        return jsonify({
            'success': True,
            'room': {
                'id': room.id,
                'room_number': room.room_number,
                'floor': room.floor,
                'room_type': room.room_type,
                'sharing_type': room.sharing_type,
                'rent_amount': room.rent_amount,
                'security_deposit': room.security_deposit,
                'facilities': room.facilities,
                'room_features': room.room_features,
                'status': room.status,
                'availability_date': room.availability_date.strftime('%Y-%m-%d') if room.availability_date else '',
                'additional_notes': room.additional_notes,
                'created_at': room.created_at.strftime('%Y-%m-%d %H:%M') if room.created_at else '',
                'tenants': tenant_info  # Add tenants information
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Add route to update room
@app.route('/edit_room/<int:room_id>', methods=['POST'])
@login_required
def edit_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Update room details
        room.room_number = request.form.get('room_number', room.room_number)
        room.floor = request.form.get('floor', room.floor)
        room.room_type = request.form.get('room_type', room.room_type)
        room.sharing_type = request.form.get('sharing_type', room.sharing_type)
        room.rent_amount = float(request.form.get('rent_amount', room.rent_amount))
        room.security_deposit = float(request.form.get('security_deposit', room.security_deposit))
        
        # Update checkbox lists
        facilities_list = request.form.getlist('facilities')
        room_features_list = request.form.getlist('room_features')
        room.facilities = ", ".join(facilities_list) if facilities_list else ""
        room.room_features = ", ".join(room_features_list) if room_features_list else ""
        
        room.status = request.form.get('status', room.status)
        room.additional_notes = request.form.get('additional_notes', room.additional_notes)
        
        # Update availability date
        availability_date_str = request.form.get('availability_date')
        if availability_date_str:
            room.availability_date = datetime.strptime(availability_date_str, '%Y-%m-%d').date()
        else:
            room.availability_date = None
        
        db.session.commit()
        flash(f'Room {room.room_number} updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating room: {str(e)}', 'error')
    
    return redirect(url_for('rooms'))

# Route to redirect to tenants page with room pre-selected
@app.route('/assign_tenant/<int:room_id>')
@login_required
def assign_tenant(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Check if room has available space
        current_tenants_count = Tenant.query.filter_by(room_id=room_id, status='Active').count()
        room_capacity = int(room.sharing_type)
        
        if current_tenants_count >= room_capacity:
            flash(f'Room {room.room_number} is already full! Maximum capacity: {room_capacity} person(s)', 'error')
            return redirect(url_for('rooms'))
        
        # Store the room ID in session to pre-select it in tenants page
        session['preselected_room_id'] = room_id
        session['auto_open_modal'] = True  # Flag to auto-open modal
        flash(f'Room {room.room_number} selected. You can now add a tenant.', 'info')
        return redirect(url_for('tenants'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('rooms'))

# Bulk delete routes (keep your existing ones)
@app.route('/delete_rooms_bulk', methods=['POST'])
@login_required
def delete_rooms_bulk():
    try:
        room_ids = request.json.get('room_ids', [])
        
        if not room_ids:
            flash('No rooms selected for deletion!', 'error')
            return jsonify({'success': False, 'message': 'No rooms selected'})
        
        # Check if any selected rooms have tenants
        rooms_with_tenants = Room.query.filter(
            Room.id.in_(room_ids),
            Room.tenants.any()
        ).all()
        
        if rooms_with_tenants:
            room_numbers = [room.room_number for room in rooms_with_tenants]
            flash(f'Cannot delete rooms {", ".join(room_numbers)} - they have active tenants!', 'error')
            return jsonify({
                'success': False, 
                'message': f'Rooms with tenants cannot be deleted: {", ".join(room_numbers)}'
            })
        
        # Delete rooms that don't have tenants
        rooms_to_delete = Room.query.filter(
            Room.id.in_(room_ids),
            ~Room.tenants.any()
        ).all()
        
        deleted_count = 0
        for room in rooms_to_delete:
            db.session.delete(room)
            deleted_count += 1
        
        db.session.commit()
        
        if deleted_count > 0:
            flash(f'Successfully deleted {deleted_count} room(s)!', 'success')
            return jsonify({'success': True, 'message': f'Deleted {deleted_count} room(s)'})
        else:
            flash('No rooms were deleted!', 'warning')
            return jsonify({'success': False, 'message': 'No rooms were deleted'})
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting rooms: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})


# Add this route for deleting individual rooms
@app.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Check if room has tenants
        if room.tenants:
            flash(f'Cannot delete room {room.room_number} - it has active tenants!', 'error')
            return redirect(url_for('rooms'))
        
        db.session.delete(room)
        db.session.commit()
        flash(f'Room {room.room_number} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting room: {str(e)}', 'error')
    
    return redirect(url_for('rooms'))

# Bulk status update route
@app.route('/update_rooms_status_bulk', methods=['POST'])
@login_required
def update_rooms_status_bulk():
    try:
        data = request.json
        room_ids = data.get('room_ids', [])
        new_status = data.get('status', 'Available')
        
        if not room_ids:
            return jsonify({'success': False, 'message': 'No rooms selected!'})
        
        if new_status not in ['Available', 'Maintenance', 'Not Available']:
            return jsonify({'success': False, 'message': 'Invalid status!'})
        
        # Update rooms status
        updated_count = 0
        for room_id in room_ids:
            room = Room.query.get(room_id)
            if room:
                # If setting to "Available", ensure room doesn't have active tenants
                if new_status == 'Available' and room.tenants:
                    # You can choose to skip these rooms or handle differently
                    continue
                
                room.status = new_status
                updated_count += 1
        
        db.session.commit()
        
        if updated_count > 0:
            return jsonify({
                'success': True, 
                'message': f'Successfully updated {updated_count} room(s) to {new_status}',
                'updated_count': updated_count
            })
        else:
            return jsonify({'success': False, 'message': 'No rooms were updated'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating rooms: {str(e)}'})


# Tenants -------------------------

@app.route('/tenants')
@login_required
def tenants():
    tenants_list = Tenant.query.all()
    available_rooms = Room.query.filter(Room.status.in_(['Available', 'Partially Occupied'])).all()
    stats = get_dashboard_stats()
    return render_template('add_tenant.html', tenants=tenants_list, available_rooms=available_rooms, stats=stats)

@app.route('/add_tenant', methods=['POST'])
@login_required
def add_tenant():
    try:
        room_id = request.form['room_id']
        room = Room.query.get(room_id)
        
        if not room:
            flash('Selected room not found!', 'error')
            return redirect(url_for('tenants'))
        
        # Check if room has available space
        current_tenants_count = Tenant.query.filter_by(room_id=room_id, status='Active').count()
        room_capacity = int(room.sharing_type)
        
        if current_tenants_count >= room_capacity:
            flash(f'Room {room.room_number} is already full! Maximum capacity: {room_capacity} person(s)', 'error')
            return redirect(url_for('tenants'))
        
        # Create tenant
        tenant = Tenant(
            full_name=request.form['full_name'],
            gender=request.form['gender'],
            phone_number=request.form['phone_number'],
            email=request.form.get('email'),
            aadhaar_number=request.form['aadhaar_number'],
            pan_number=request.form.get('pan_number'), 
            emergency_contact=request.form['emergency_contact'],
            address_line1=request.form['address_line1'],
            address_line2=request.form.get('address_line2'), 
            city=request.form['city'],
            state=request.form['state'],
            pin_code=request.form.get('pin_code'), 
            room_id=room_id,
            bed_number=request.form.get('bed_number'),
            move_in_date=datetime.strptime(request.form['move_in_date'], '%Y-%m-%d').date(),
            agreement_period=int(request.form['agreement_period']),
            monthly_rent=float(request.form['monthly_rent']),
            security_deposit_paid=float(request.form['security_deposit'])
        )
        
        if request.form.get('date_of_birth'): 
            tenant.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        
        # Update room status based on occupancy
        current_tenants_count_after_add = current_tenants_count + 1
        
        if current_tenants_count_after_add == room_capacity:
            room.status = 'Occupied'
        elif current_tenants_count_after_add < room_capacity and current_tenants_count_after_add > 0:
            room.status = 'Partially Occupied'
        
        db.session.add(tenant)
        db.session.commit()
        
        flash(f'Tenant {tenant.full_name} added successfully to Room {room.room_number}!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding tenant: {str(e)}', 'error')
    
    return redirect(url_for('tenants'))

# Add route to get tenant details for tenant management
@app.route('/api/tenant/<int:tenant_id>')
@login_required
def get_tenant_details_new(tenant_id):
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        room = Room.query.get(tenant.room_id)
        
        return jsonify({
            'success': True,
            'tenant': {
                'id': tenant.id,
                'full_name': tenant.full_name,
                'gender': tenant.gender,
                'phone_number': tenant.phone_number,
                'email': tenant.email,
                'aadhaar_number': tenant.aadhaar_number,
                'pan_number': tenant.pan_number,
                'emergency_contact': tenant.emergency_contact,
                'address_line1': tenant.address_line1,
                'address_line2': tenant.address_line2,
                'city': tenant.city,
                'state': tenant.state,
                'pin_code': tenant.pin_code,
                'room_id': tenant.room_id,
                'bed_number': tenant.bed_number,
                'move_in_date': tenant.move_in_date.strftime('%Y-%m-%d') if tenant.move_in_date else '',
                'date_of_birth': tenant.date_of_birth.strftime('%Y-%m-%d') if tenant.date_of_birth else '',
                'agreement_period': tenant.agreement_period,
                'monthly_rent': tenant.monthly_rent,
                'security_deposit_paid': tenant.security_deposit_paid,
                'status': tenant.status,
                'room_number': room.room_number if room else 'N/A',
                'room_type': room.room_type if room else 'N/A'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Add route to remove tenant
@app.route('/remove_tenant/<int:tenant_id>', methods=['POST'])
@login_required
def remove_tenant(tenant_id):
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        room = Room.query.get(tenant.room_id)
        
        # Store tenant info for flash message
        tenant_name = tenant.full_name
        room_number = room.room_number if room else 'N/A'
        
        # First, handle related complaints by deleting them
        complaints = Complaint.query.filter_by(tenant_id=tenant_id).all()
        for complaint in complaints:
            db.session.delete(complaint)
        
        # Also handle payments related to this tenant
        payments = Payment.query.filter_by(tenant_id=tenant_id).all()
        for payment in payments:
            db.session.delete(payment)
        
        # Update room status based on remaining tenants
        if room:
            remaining_tenants = Tenant.query.filter_by(room_id=room.id, status='Active').count() - 1
            
            if remaining_tenants == 0:
                room.status = 'Available'
            elif remaining_tenants < int(room.sharing_type):
                room.status = 'Partially Occupied'
        
        # Remove tenant
        db.session.delete(tenant)
        db.session.commit()
        
        flash(f'Tenant {tenant_name} has been removed from Room {room_number}!', 'success')
        return jsonify({'success': True, 'message': f'Tenant {tenant_name} removed successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Add route to update tenant
@app.route('/edit_tenant/<int:tenant_id>', methods=['POST'])
@login_required
def edit_tenant(tenant_id):
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        
        # Update tenant details
        tenant.full_name = request.form.get('full_name', tenant.full_name)
        tenant.gender = request.form.get('gender', tenant.gender)
        tenant.phone_number = request.form.get('phone_number', tenant.phone_number)
        tenant.email = request.form.get('email', tenant.email)
        tenant.aadhaar_number = request.form.get('aadhaar_number', tenant.aadhaar_number)
        tenant.pan_number = request.form.get('pan_number', tenant.pan_number)
        tenant.emergency_contact = request.form.get('emergency_contact', tenant.emergency_contact)
        tenant.address_line1 = request.form.get('address_line1', tenant.address_line1)
        tenant.address_line2 = request.form.get('address_line2', tenant.address_line2)
        tenant.city = request.form.get('city', tenant.city)
        tenant.state = request.form.get('state', tenant.state)
        tenant.pin_code = request.form.get('pin_code', tenant.pin_code)
        tenant.bed_number = request.form.get('bed_number', tenant.bed_number)
        tenant.monthly_rent = float(request.form.get('monthly_rent', tenant.monthly_rent))
        tenant.security_deposit_paid = float(request.form.get('security_deposit_paid', tenant.security_deposit_paid))
        tenant.agreement_period = int(request.form.get('agreement_period', tenant.agreement_period))
        
        # Update dates
        if request.form.get('move_in_date'):
            tenant.move_in_date = datetime.strptime(request.form['move_in_date'], '%Y-%m-%d').date()
        
        if request.form.get('date_of_birth'):
            tenant.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Tenant {tenant.full_name} updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Add route to get room details for tenant form
@app.route('/api/room_details/<int:room_id>')
@login_required
def get_room_details_for_tenant(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        current_tenants = Tenant.query.filter_by(room_id=room_id, status='Active').count()
        available_beds = int(room.sharing_type) - current_tenants
        
        return jsonify({
            'success': True,
            'room': {
                'room_number': room.room_number,
                'room_type': room.room_type,
                'sharing_type': room.sharing_type,
                'rent_amount': room.rent_amount,
                'current_tenants': current_tenants,
                'available_beds': available_beds,
                'facilities': room.facilities
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Payments -------------------------

@app.route('/payments')
@login_required
def payments():
    payments_list = Payment.query.order_by(Payment.payment_date.desc()).all()
    tenants_list = Tenant.query.filter_by(status='Active').all()
    stats = get_dashboard_stats()
    
    # Calculate monthly collection
    from sqlalchemy import func
    from datetime import datetime

    # Current month calculations
    current_month = datetime.now().strftime('%B %Y')
    monthly_payments = Payment.query.filter(
        func.lower(Payment.payment_for) == current_month.lower(),
        Payment.payment_type == 'Rent'
    ).all()

    total_collected = sum(p.amount for p in monthly_payments)
    current_month_total = total_collected
    
    # Total collected overall
    total_collected_all = sum(p.amount for p in Payment.query.all())
    
    total_expected = sum(t.monthly_rent for t in tenants_list)
    collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
    
    return render_template('add_payment.html', 
                         payments=payments_list,
                         tenants=tenants_list,
                         stats=stats,
                         total_collected=total_collected_all,
                         current_month_total=current_month_total,
                         total_expected=total_expected,
                         collection_rate=collection_rate)

@app.route('/add_payment', methods=['POST'])
@login_required
def add_payment():
    try:
        # Fetch form data
        tenant_id = request.form['tenant_id']
        payment_type = request.form['payment_type']
        payment_for = request.form['payment_for']
        amount = float(request.form['amount'])
        payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
        payment_method = request.form['payment_method']
        reference_number = request.form.get('reference_number')
        additional_notes = request.form.get('additional_notes')

        # Ensure Month-Year format consistency
        try:
            payment_month = datetime.strptime(payment_for[:7], '%Y-%m')
            payment_for = payment_month.strftime('%B %Y')
        except Exception:
            pass  # if already in "November 2025" format, continue

        # Create payment record
        payment = Payment(
            tenant_id=tenant_id,
            payment_type=payment_type,
            payment_for=payment_for,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            additional_notes=additional_notes
        )

        db.session.add(payment)

        # Update tenant pending rent if it's a rent payment
        tenant = Tenant.query.get(tenant_id)
        if tenant and payment_type.lower() == 'rent':
            tenant.pending_rent = max(0, getattr(tenant, 'pending_rent', tenant.monthly_rent) - amount)

        db.session.commit()

        flash(f'Payment of ₹{amount} recorded successfully for {payment_for}!', 'success')
        return redirect(url_for('payments'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'error')
        return redirect(url_for('payments'))

@app.route('/delete_payment/<int:payment_id>', methods=['DELETE'])
@login_required
def delete_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        payment_amount = payment.amount
        tenant_name = payment.tenant.full_name
        
        # If it's a rent payment, adjust tenant's pending rent
        if payment.payment_type.lower() == 'rent':
            tenant = payment.tenant
            tenant.pending_rent = getattr(tenant, 'pending_rent', 0) + payment_amount
        
        db.session.delete(payment)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Payment of ₹{payment_amount} for {tenant_name} has been deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_all_payments', methods=['POST'])
@login_required
def delete_all_payments():
    try:
        # Reset pending rent for all tenants
        tenants = Tenant.query.all()
        for tenant in tenants:
            tenant.pending_rent = tenant.monthly_rent
        
        # Delete all payments
        db.session.query(Payment).delete()
        db.session.commit()
        
        flash('All payments have been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting payments: {e}', 'error')

    return redirect(url_for('payments'))

# Add this route to your app.py

@app.route('/api/payment/<int:payment_id>')
@login_required
def get_payment_details(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)
        tenant = Tenant.query.get(payment.tenant_id)
        room = Room.query.get(tenant.room_id) if tenant else None
        
        return jsonify({
            'success': True,
            'payment': {
                'id': payment.id,
                'tenant_name': tenant.full_name if tenant else 'N/A',
                'tenant_phone': tenant.phone_number if tenant else 'N/A',
                'room_number': room.room_number if room else 'N/A',
                'room_type': room.room_type if room else 'N/A',
                'payment_type': payment.payment_type,
                'payment_for': payment.payment_for,
                'amount': payment.amount,
                'payment_date': payment.payment_date.strftime('%d %B %Y'),
                'payment_method': payment.payment_method,
                'reference_number': payment.reference_number or 'Not provided',
                'additional_notes': payment.additional_notes or 'No additional notes',
                'created_at': payment.created_at.strftime('%d %B %Y at %I:%M %p') if payment.created_at else 'N/A',
                'status': 'Completed'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Complaints -------------------------

@app.route('/complaints')
@login_required
def complaints():
    complaints_list = Complaint.query.order_by(Complaint.created_at.desc()).all()
    tenants_list = Tenant.query.all()
    
    # Complaint statistics
    open_complaints = Complaint.query.filter_by(status='Open').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    
    return render_template('complaints.html',
                         complaints=complaints_list,
                         tenants=tenants_list,
                         open_complaints=open_complaints,
                         in_progress=in_progress,
                         resolved=resolved)

@app.route('/add_complaint', methods=['POST'])
@login_required
def add_complaint():
    try:
        complaint = Complaint(
            tenant_id=request.form['tenant_id'],
            room_id=request.form['room_id'],
            category=request.form['category'],
            priority=request.form['priority'],
            description=request.form['description'],
            assigned_to=request.form.get('assigned_to')
        )
        
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint registered successfully!', 'success')
    except Exception as e:
        flash(f'Error registering complaint: {str(e)}', 'error')
    
    return redirect(url_for('complaints'))

@app.route('/update_complaint_status/<int:complaint_id>', methods=['POST'])
@login_required
def update_complaint_status(complaint_id):
    try:
        complaint = Complaint.query.get_or_404(complaint_id)
        complaint.status = request.form['status']
        db.session.commit()
        flash('Complaint status updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating complaint: {str(e)}', 'error')
    
    return redirect(url_for('complaints'))

@app.route('/delete_complaint/<int:complaint_id>', methods=['POST'])
@login_required
def delete_complaint(complaint_id):
    try:
        complaint = Complaint.query.get_or_404(complaint_id)
        db.session.delete(complaint)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Complaint deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/complaint/<int:complaint_id>')
@login_required
def get_complaint_details(complaint_id):
    try:
        complaint = Complaint.query.get_or_404(complaint_id)
        
        # Calculate expected resolution based on priority
        resolution_times = {
            'High': '24 hours',
            'Medium': '48 hours', 
            'Low': '7 days'
        }
        
        return jsonify({
            'success': True,
            'complaint': {
                'id': complaint.id,
                'tenant_name': complaint.tenant.full_name,
                'room_number': complaint.room.room_number,
                'category': complaint.category,
                'priority': complaint.priority,
                'status': complaint.status,
                'assigned_to': complaint.assigned_to,
                'description': complaint.description,
                'created_date': complaint.created_at.strftime('%d/%m/%Y'),
                'created_time': complaint.created_at.strftime('%H:%M'),
                'expected_resolution': resolution_times.get(complaint.priority, 'N/A')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Reports -------------------------

# Reports -------------------------

@app.route('/reports')
@login_required
def reports():
    stats = get_dashboard_stats()
    
    # Get payment counters
    payment_counters = get_payment_counters()
    
    # Financial data for charts
    months = []
    revenue_data = []
    
    for i in range(6):
        month = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_str = month.strftime('%B %Y')
        months.append(month_str)
        
        monthly_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
            db.func.strftime('%Y-%m', Payment.created_at) == month.strftime('%Y-%m')
        ).scalar() or 0
        revenue_data.append(monthly_revenue)
    
    months.reverse()
    revenue_data.reverse()
    
    # Room occupancy data
    room_types = ['Single', 'Sharing', 'Suite']
    occupancy_by_type = []
    for room_type in room_types:
        total = Room.query.filter_by(room_type=room_type).count()
        occupied = Room.query.filter_by(room_type=room_type, status='Occupied').count()
        occupancy_by_type.append({
            'type': room_type,
            'total': total,
            'occupied': occupied
        })
    
    # Get tenants for demographics
    tenants_list = Tenant.query.all()
    
    # Get defaulters for rent collection report
    current_month = datetime.now().strftime('%B %Y')
    defaulters = []
    for tenant in Tenant.query.filter_by(status='Active').all():
        paid = Payment.query.filter_by(
            tenant_id=tenant.id,
            payment_for=current_month,
            payment_type='Rent'
        ).first()
        if not paid:
            defaulters.append(tenant)
    
    return render_template('reports.html',
                         stats=stats,
                         months=months,
                         revenue_data=revenue_data,
                         occupancy_by_type=occupancy_by_type,
                         tenants=tenants_list,
                         defaulters=defaulters,
                         payment_counters=payment_counters)

# API endpoints for dynamic data
@app.route('/api/tenant_details/<int:tenant_id>')
@login_required
def get_tenant_details(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    room = Room.query.get(tenant.room_id)
    return jsonify({
        'name': tenant.full_name,
        'room': room.room_number if room else 'N/A',
        'monthly_rent': tenant.monthly_rent,
        'pending_dues': calculate_pending_dues(tenant_id)
    })

@app.route('/api/available_rooms')
@login_required
def get_available_rooms():
    rooms = Room.query.filter_by(status='Available').all()
    return jsonify([{
        'id': room.id,
        'room_number': room.room_number,
        'floor': room.floor,
        'room_type': room.room_type,
        'rent_amount': room.rent_amount
    } for room in rooms])

def calculate_pending_dues(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return 0
    
    # Simple calculation - in real app, you'd want more sophisticated logic
    current_month = datetime.now().strftime('%B %Y')
    paid_this_month = Payment.query.filter_by(
        tenant_id=tenant_id,
        payment_for=current_month,
        payment_type='Rent'
    ).first()
    
    return 0 if paid_this_month else tenant.monthly_rent

# Add these helper functions for payment counters
def get_weekly_payments():
    """Get total payments for the current week"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    
    weekly_payments = Payment.query.filter(
        Payment.payment_date >= start_of_week,
        Payment.payment_date <= end_of_week
    ).all()
    
    return sum(p.amount for p in weekly_payments)

def get_monthly_payments():
    """Get total payments for the current month"""
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    
    # Calculate end of month
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    monthly_payments = Payment.query.filter(
        Payment.payment_date >= start_of_month,
        Payment.payment_date <= end_of_month
    ).all()
    
    return sum(p.amount for p in monthly_payments)

def get_yearly_payments():
    """Get total payments for the current year"""
    today = datetime.now().date()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    
    yearly_payments = Payment.query.filter(
        Payment.payment_date >= start_of_year,
        Payment.payment_date <= end_of_year
    ).all()
    
    return sum(p.amount for p in yearly_payments)

def get_payment_counters():
    """Get all payment counters for weekly, monthly, yearly"""
    return {
        'weekly': get_weekly_payments(),
        'monthly': get_monthly_payments(),
        'yearly': get_yearly_payments(),
        'all_time': sum(p.amount for p in Payment.query.all())
    }








if __name__ == '__main__':
    app.run(debug=True)
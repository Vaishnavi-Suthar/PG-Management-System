# **PG Management System**

A comprehensive web-based application designed to digitize and automate daily operations of Paying Guest (PG) accommodation facilities.
This system manages **rooms, tenants, payments, occupancy tracking, and reports**, offering both simplicity and efficiency for administrators.

---

## **Features**

### 🔐 **Authentication**

* Secure Admin Login
* Session-based access control

### 🏠 **Room Management**

* Add, update, delete rooms
* Manage room categories (Single/Double/AC/Non-AC)
* Track real-time availability (Available / Occupied)

### 👨‍💼 **Tenant (Guest) Management**

* Add tenant details with ID proof
* Allocate rooms
* Track check-in / check-out
* Maintain complete tenant history

### 💸 **Payment Management**

* Record rent payments
* Track paid & pending payments
* Monthly payment logs

### 📊 **Reports & Dashboard**

* Room occupancy reports
* Tenant records
* Payment summaries
* Real-time status overview

---

## **Technology Stack**

| Layer        | Technologies Used                                     |
| ------------ | ----------------------------------------------------- |
| **Frontend** | HTML, CSS, JavaScript (after converting from Tkinter) |
| **Backend**  | Python Flask                                          |
| **Database** | SQLite                                                |
| **Tools**    | Visual Studio 2022                                    |

---

## **Installation**

### **Prerequisites**

* Python 3.8+
* pip (Python package manager)

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/pg-management-system.git
cd pg-management-system
```

### **2. Install Required Packages**

```bash
pip install -r requirements.txt
```

### **3. Run the Application**

```bash
python app.py
```

The system will run on:

```
http://127.0.0.1:5000
```

---

## **Usage**

### **Admin Panel**

1. Login using admin credentials
2. Manage rooms and categories
3. Add tenants and allocate rooms
4. Record payments or scan QR for rent
5. View reports and history

---

## **Project Structure**

```
pg-management-system/
│── app.py               # Main Flask application
│── static/              # CSS, JS, Images
│── templates/           # HTML templates
│── database.db          # SQLite database
│── requirements.txt     # Dependencies
│── README.md            # Description
```


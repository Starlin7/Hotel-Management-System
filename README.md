# Hotel Management System

A web-based Hotel Management System developed using **Python, Flask, and MySQL** to simplify hotel operations, manage room reservations, maintain customer information, and handle administrative activities.

The application provides separate interfaces for users and administrators, allowing hotel operations to be managed through a centralized system.

## 🚀 Features

### 👤 User Module
- User registration and login.
- View available rooms.
- Book hotel rooms.
- View reservation history.
- Submit feedback.
- Secure logout functionality.

### 🛠️ Admin Module
- Admin authentication.
- Admin dashboard with hotel information and statistics.
- Manage room types and rooms.
- Manage reservations.
- Manage room inventory.
- Manage departments and employees.
- Manage payments and invoices.
- Manage hotel services.
- Manage housekeeping activities.
- View and manage customer feedback.
- Manage discounts and hotel policies.

## 🧰 Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| MySQL | Relational database management |
| MySQL Connector | Python-MySQL connectivity |
| HTML | Web page structure |
| CSS | Styling and layout |
| JavaScript | Client-side functionality |

## 🗄️ Database Structure

The project uses a MySQL relational database named `hotel_management`.

The database contains 15 tables:

1. `users` – Stores customer information.
2. `admins` – Stores administrator details.
3. `rooms` – Stores room information.
4. `room_types` – Maintains different room categories.
5. `reservations` – Stores customer booking details.
6. `room_inventory` – Maintains room inventory information.
7. `employees` – Stores employee details.
8. `departments` – Maintains hotel departments.
9. `payments` – Stores payment information.
10. `invoices` – Maintains invoice records.
11. `services` – Stores hotel service information.
12. `housekeeping` – Manages housekeeping activities.
13. `feedback` – Stores customer feedback.
14. `discounts` – Maintains discount information.
15. `hotel_policies` – Stores hotel policies.

The SQL database file is included in this repository.

**Database file:** `hotel_management_data.sql`

## ⚙️ Installation and Setup

Follow these steps to run the project on your local machine.

### Prerequisites

Make sure you have installed:

- Python 3.x
- MySQL Server
- MySQL Workbench (recommended)
- Visual Studio Code or any Python IDE

### Step 1: Clone the Repository

Open your terminal and execute:

```bash
git clone https://github.com/Starlin7/Hotel-Management-System.git
```

Navigate to the project directory:

```bash
cd Hotel-Management-System
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install Flask mysql-connector-python
```

### Step 4: Set Up the MySQL Database

1. Open MySQL Workbench.
2. Connect to your local MySQL Server.
3. Open the `hotel_management_data.sql` file from the project folder.
4. Execute the SQL script.
5. Verify that the `hotel_management` database and its tables have been created.

### Step 5: Configure Database Connection

Open `app.py` and update the MySQL connection configuration according to your local MySQL setup.

```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="hotel_management"
)
```

### Step 6: Run the Application

Execute:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000/
```

The Hotel Management System should now be running locally.

## 📁 Project Structure

```text
Hotel-Management-System/
│
├── app.py
├── hotel_management_data.sql
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │
│   └── images/
│       ├── banner.jpg
│       └── banner2.jpg
│
└── templates/
    ├── admin_dashboard.html
    ├── admin_discounts.html
    ├── admin_employees.html
    ├── admin_feedback.html
    ├── admin_hotel_policies.html
    ├── admin_housekeeping.html
    ├── admin_invoices.html
    ├── admin_login.html
    ├── admin_payments.html
    ├── admin_room_types.html
    ├── admin_rooms.html
    ├── admin_services.html
    ├── base.html
    ├── edit_employee.html
    ├── edit_room.html
    ├── edit_room_type.html
    ├── index.html
    ├── login.html
    ├── my_reservations.html
    ├── reserve.html
    ├── rooms.html
    ├── submit_feedback.html
    └── user_submit_feedback.html
```

## 🎯 Project Objective

The main objective of this project is to develop a centralized hotel management application that simplifies room reservations, customer management, employee administration, payment records, and other hotel-related operations.

It also provides practical experience in Python web development, relational database management, SQL queries, and Flask-MySQL integration.

## 🔮 Future Enhancements

- Integration of an online payment gateway.
- Improved authentication and password security.
- Advanced reservation validation and availability management.
- Enhanced reporting and analytics.
- Improved responsive user interface.

## 👨‍💻 Author

**Starlin Pereira**

- GitHub: https://github.com/Starlin7
- LinkedIn: https://www.linkedin.com/in/starlinpereira

---

⭐ If you find this project interesting, feel free to explore the repository!

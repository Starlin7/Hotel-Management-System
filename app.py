from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "a_very_secure_random_string_here"  # Replace with a strong secret key

# MySQL connection configuration – update with your real credentials
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hotel_management"
)
cursor = db.cursor(dictionary=True)

###############################################
#              USER OPERATIONS                #
###############################################

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# User Login & Logout
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
         username = request.form["username"]
         password = request.form["password"]
         query = "SELECT * FROM users WHERE username = %s AND password = %s"
         cursor.execute(query, (username, password))
         user = cursor.fetchone()
         if user:
             session["user"] = user
             flash("User login successful!", "success")
             return redirect(url_for("rooms"))
         else:
             flash("Invalid user credentials. Please try again.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))

# Display available rooms to users
@app.route("/rooms")
def rooms():
    query = "SELECT * FROM rooms WHERE status = 'Available'"
    cursor.execute(query)
    rooms = cursor.fetchall()
    return render_template("rooms.html", rooms=rooms)

# User reservation: create a new reservation and update room status
@app.route("/reserve/<room_id>", methods=["GET", "POST"])
def reserve(room_id):
    if request.method == "POST":
        user = session.get("user")
        if not user:
            flash("Please log in to make a reservation", "danger")
            return redirect(url_for("login"))
        check_in = request.form["check_in_date"]
        check_out = request.form["check_out_date"]

        # Retrieve the room's price; this enforces the relationship between rooms and reservations
        cursor.execute("SELECT price_per_night FROM rooms WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        if room:
            price = room["price_per_night"]
            d1 = datetime.strptime(check_in, "%Y-%m-%d")
            d2 = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (d2 - d1).days
            amount = price * nights

            # Generate a reservation ID (in production, use a better unique ID)
            reservation_id = "RSV" + str(random.randint(1000, 9999))
            insert_query = """
                INSERT INTO reservations 
                (reservation_id, user_id, room_id, check_in_date, check_out_date, amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (reservation_id, user["user_id"], room_id, check_in, check_out, amount, "Confirmed"))
            db.commit()

            # Update the room status to 'Occupied'
            cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_id = %s", (room_id,))
            db.commit()

            flash("Reservation successful!", "success")
            return redirect(url_for("rooms"))
        else:
            flash("Room not found.", "danger")
    return render_template("reserve.html", room_id=room_id)

# View user's own reservations
@app.route("/my_reservations")
def my_reservations():
    user = session.get("user")
    if not user:
        flash("Please log in to view your reservations", "danger")
        return redirect(url_for("login"))
    query = "SELECT * FROM reservations WHERE user_id = %s"
    cursor.execute(query, (user["user_id"],))
    reservations = cursor.fetchall()
    return render_template("my_reservations.html", reservations=reservations)
#feedback
@app.route("/feedback/submit", methods=["GET", "POST"])
def user_submit_feedback():
    user = session.get("user")
    if not user:
        flash("Please log in to submit feedback", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        # Generate a feedback ID; in production, use a more robust method
        feedback_id = "FB" + str(random.randint(1000, 9999))
        reservation_id = request.form["reservation_id"]  # You might want to validate that the reservation belongs to the user
        rating = request.form["rating"]
        comments = request.form["comments"]
        feedback_date = datetime.now().strftime("%Y-%m-%d")
        query = """INSERT INTO feedback (feedback_id, reservation_id, rating, comments, feedback_date)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (feedback_id, reservation_id, rating, comments, feedback_date))
        db.commit()
        flash("Feedback submitted. Thank you!", "success")
        return redirect(url_for("my_reservations"))
    return render_template("user_submit_feedback.html")


###############################################
#            ADMIN OPERATIONS                 #
###############################################

# Admin Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
         email = request.form["email"]
         password = request.form["password"]
         query = "SELECT * FROM admins WHERE email = %s AND password = %s"
         cursor.execute(query, (email, password))
         admin = cursor.fetchone()
         if admin:
             session["admin"] = admin
             flash("Admin login successful!", "success")
             return redirect(url_for("admin_dashboard"))
         else:
             flash("Invalid admin credentials. Please try again.", "danger")
    return render_template("admin_login.html")

# Admin Dashboard (overview)
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    # Get the dynamic counts from the database
    cursor.execute("SELECT COUNT(*) as total_rooms FROM rooms")
    total_rooms = cursor.fetchone()["total_rooms"]
    cursor.execute("SELECT COUNT(*) as total_reservations FROM reservations")
    total_reservations = cursor.fetchone()["total_reservations"]
    
    return render_template("admin_dashboard.html", 
                           total_rooms=total_rooms, 
                           total_reservations=total_reservations)


# ----- Module: Room Types (maintaining FK with Rooms) -----

@app.route("/admin/room_types")
def admin_room_types():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM room_types")
    room_types = cursor.fetchall()
    return render_template("admin_room_types.html", room_types=room_types)

@app.route("/admin/room_types/add", methods=["POST"])
def add_room_type():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    room_type_id = request.form["room_type_id"]
    type_name = request.form["type_name"]
    description = request.form["description"]
    query = "INSERT INTO room_types (room_type_id, type_name, description) VALUES (%s, %s, %s)"
    cursor.execute(query, (room_type_id, type_name, description))
    db.commit()
    flash("Room type added successfully!", "success")
    return redirect(url_for("admin_room_types"))

@app.route("/admin/room_types/edit/<room_type_id>", methods=["GET", "POST"])
def edit_room_type(room_type_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    if request.method == "POST":
         type_name = request.form["type_name"]
         description = request.form["description"]
         query = "UPDATE room_types SET type_name=%s, description=%s WHERE room_type_id=%s"
         cursor.execute(query, (type_name, description, room_type_id))
         db.commit()
         flash("Room type updated successfully!", "success")
         return redirect(url_for("admin_room_types"))
    else:
         cursor.execute("SELECT * FROM room_types WHERE room_type_id=%s", (room_type_id,))
         room_type = cursor.fetchone()
         return render_template("edit_room_type.html", room_type=room_type)

@app.route("/admin/room_types/delete/<room_type_id>")
def delete_room_type(room_type_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("DELETE FROM room_types WHERE room_type_id=%s", (room_type_id,))
    db.commit()
    flash("Room type deleted successfully!", "success")
    return redirect(url_for("admin_room_types"))

# ----- Module: Rooms (linked to Room Types & used in Reservations) -----

@app.route("/admin/rooms")
def admin_rooms():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    return render_template("admin_rooms.html", rooms=rooms)

@app.route("/admin/rooms/add", methods=["POST"])
def add_room():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    room_id = request.form["room_id"]
    room_number = request.form["room_number"]
    room_type_id = request.form["room_type_id"]
    floor = request.form["floor"]
    capacity = request.form["capacity"]
    price_per_night = request.form["price_per_night"]
    status = request.form["status"]
    query = """INSERT INTO rooms (room_id, room_number, room_type_id, floor, capacity, price_per_night, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (room_id, room_number, room_type_id, floor, capacity, price_per_night, status))
    db.commit()
    flash("Room added successfully!", "success")
    return redirect(url_for("admin_rooms"))

@app.route("/admin/rooms/edit/<room_id>", methods=["GET", "POST"])
def edit_room(room_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    if request.method == "POST":
         room_number = request.form["room_number"]
         room_type_id = request.form["room_type_id"]
         floor = request.form["floor"]
         capacity = request.form["capacity"]
         price_per_night = request.form["price_per_night"]
         status = request.form["status"]
         query = """UPDATE rooms SET room_number=%s, room_type_id=%s, floor=%s, capacity=%s, price_per_night=%s, status=%s 
                    WHERE room_id=%s"""
         cursor.execute(query, (room_number, room_type_id, floor, capacity, price_per_night, status, room_id))
         db.commit()
         flash("Room updated successfully!", "success")
         return redirect(url_for("admin_rooms"))
    else:
         cursor.execute("SELECT * FROM rooms WHERE room_id=%s", (room_id,))
         room = cursor.fetchone()
         return render_template("edit_room.html", room=room)

@app.route("/admin/rooms/delete/<room_id>")
def delete_room(room_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("DELETE FROM rooms WHERE room_id=%s", (room_id,))
    db.commit()
    flash("Room deleted successfully!", "success")
    return redirect(url_for("admin_rooms"))

# ----- Module: Reservations (linked to Users and Rooms) -----

@app.route("/admin/reservations")
def admin_reservations():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    return render_template("admin_reservations.html", reservations=reservations)

# Optionally, you can add routes for updating reservation status (e.g., to mark a reservation as canceled or completed)
@app.route("/admin/reservations/edit/<reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    if request.method == "POST":
         # For example, updating status only
         status = request.form["status"]
         query = "UPDATE reservations SET status=%s WHERE reservation_id=%s"
         cursor.execute(query, (status, reservation_id))
         db.commit()
         flash("Reservation updated successfully!", "success")
         return redirect(url_for("admin_reservations"))
    else:
         cursor.execute("SELECT * FROM reservations WHERE reservation_id=%s", (reservation_id,))
         reservation = cursor.fetchone()
         return render_template("edit_reservation.html", reservation=reservation)

@app.route("/admin/reservations/delete/<reservation_id>")
def delete_reservation(reservation_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("DELETE FROM reservations WHERE reservation_id=%s", (reservation_id,))
    db.commit()
    flash("Reservation deleted successfully!", "success")
    return redirect(url_for("admin_reservations"))

# ----- Module: Room Inventory (linked to Rooms) -----

@app.route("/admin/room_inventory")
def admin_room_inventory():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM room_inventory")
    inventory = cursor.fetchall()
    return render_template("admin_room_inventory.html", inventory=inventory)

# ----- Module: Departments -----

@app.route("/admin/departments")
def admin_departments():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    return render_template("admin_departments.html", departments=departments)

@app.route("/admin/departments/add", methods=["POST"])
def add_department():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    department_id = request.form["department_id"]
    department_name = request.form["department_name"]
    query = "INSERT INTO departments (department_id, department_name) VALUES (%s, %s)"
    cursor.execute(query, (department_id, department_name))
    db.commit()
    flash("Department added successfully!", "success")
    return redirect(url_for("admin_departments"))

# ----- Module: Employees (linked to Users and Departments) -----

@app.route("/admin/employees")
def admin_employees():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template("admin_employees.html", employees=employees)

@app.route("/admin/employees/add", methods=["POST"])
def add_employee():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    employee_id = request.form["employee_id"]
    user_id = request.form["user_id"]  # Must already exist in users table
    department_id = request.form["department_id"]
    position = request.form["position"]
    hire_date = request.form["hire_date"]
    query = "INSERT INTO employees (employee_id, user_id, department_id, position, hire_date) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (employee_id, user_id, department_id, position, hire_date))
    db.commit()
    flash("Employee added successfully!", "success")
    return redirect(url_for("admin_employees"))

@app.route("/admin/employees/edit/<employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    if request.method == "POST":
         user_id = request.form["user_id"]
         department_id = request.form["department_id"]
         position = request.form["position"]
         hire_date = request.form["hire_date"]
         query = "UPDATE employees SET user_id=%s, department_id=%s, position=%s, hire_date=%s WHERE employee_id=%s"
         cursor.execute(query, (user_id, department_id, position, hire_date, employee_id))
         db.commit()
         flash("Employee updated successfully!", "success")
         return redirect(url_for("admin_employees"))
    else:
         cursor.execute("SELECT * FROM employees WHERE employee_id=%s", (employee_id,))
         employee = cursor.fetchone()
         return render_template("edit_employee.html", employee=employee)

@app.route("/admin/employees/delete/<employee_id>")
def delete_employee(employee_id):
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
    db.commit()
    flash("Employee deleted successfully!", "success")
    return redirect(url_for("admin_employees"))

# ----- Module: Payments (linked to Reservations) -----

@app.route("/admin/payments")
def admin_payments():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    return render_template("admin_payments.html", payments=payments)

@app.route("/admin/payments/add", methods=["POST"])
def add_payment():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    payment_id = request.form["payment_id"]
    reservation_id = request.form["reservation_id"]  # Must reference an existing reservation
    amount = request.form["amount"]
    payment_date = request.form["payment_date"]
    payment_method = request.form["payment_method"]
    status = request.form["status"]
    query = """INSERT INTO payments (payment_id, reservation_id, amount, payment_date, payment_method, status)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (payment_id, reservation_id, amount, payment_date, payment_method, status))
    db.commit()
    flash("Payment added successfully!", "success")
    return redirect(url_for("admin_payments"))

# ----- Module: Invoices (linked to Reservations) -----

@app.route("/admin/invoices")
def admin_invoices():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()
    return render_template("admin_invoices.html", invoices=invoices)

@app.route("/admin/invoices/add", methods=["POST"])
def add_invoice():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    invoice_id = request.form["invoice_id"]
    reservation_id = request.form["reservation_id"]
    total_amount = request.form["total_amount"]
    issued_date = request.form["issued_date"]
    due_date = request.form["due_date"]
    query = """INSERT INTO invoices (invoice_id, reservation_id, total_amount, issued_date, due_date)
               VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (invoice_id, reservation_id, total_amount, issued_date, due_date))
    db.commit()
    flash("Invoice added successfully!", "success")
    return redirect(url_for("admin_invoices"))

# ----- Module: Services -----

@app.route("/admin/services")
def admin_services():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    return render_template("admin_services.html", services=services)

@app.route("/admin/services/add", methods=["POST"])
def add_service():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    service_id = request.form["service_id"]
    service_name = request.form["service_name"]
    description = request.form["description"]
    price = request.form["price"]
    query = "INSERT INTO services (service_id, service_name, description, price) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (service_id, service_name, description, price))
    db.commit()
    flash("Service added successfully!", "success")
    return redirect(url_for("admin_services"))

# ----- Module: Housekeeping (linked to Rooms and Services) -----

@app.route("/admin/housekeeping")
def admin_housekeeping():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM housekeeping")
    housekeeping = cursor.fetchall()
    return render_template("admin_housekeeping.html", housekeeping=housekeeping)

@app.route("/admin/housekeeping/add", methods=["POST"])
def add_housekeeping():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    housekeeping_id = request.form["housekeeping_id"]
    room_id = request.form["room_id"]  # Must reference an existing room
    service_id = request.form["service_id"]  # Must reference an existing service
    service_date = request.form["service_date"]
    query = "INSERT INTO housekeeping (housekeeping_id, room_id, service_id, service_date) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (housekeeping_id, room_id, service_id, service_date))
    db.commit()
    flash("Housekeeping record added successfully!", "success")
    return redirect(url_for("admin_housekeeping"))

# ----- Module: Feedback (linked to Reservations) -----

@app.route("/admin/feedback")
def admin_feedback():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM feedback")
    feedback = cursor.fetchall()
    return render_template("admin_feedback.html", feedback=feedback)

# (Optionally, users could submit feedback too; for admin, they might only review or delete.)
@app.route("/feedback/submit", methods=["GET", "POST"])
def submit_feedback():
    user = session.get("user")
    if not user:
        flash("Please log in to submit feedback", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
         feedback_id = "FB" + str(random.randint(1000, 9999))
         reservation_id = request.form["reservation_id"]  # Ensure this reservation belongs to the user
         rating = request.form["rating"]
         comments = request.form["comments"]
         feedback_date = datetime.now().strftime("%Y-%m-%d")
         query = "INSERT INTO feedback (feedback_id, reservation_id, rating, comments, feedback_date) VALUES (%s, %s, %s, %s, %s)"
         cursor.execute(query, (feedback_id, reservation_id, rating, comments, feedback_date))
         db.commit()
         flash("Feedback submitted. Thank you!", "success")
         return redirect(url_for("my_reservations"))
    return render_template("submit_feedback.html")

# ----- Module: Discounts -----

@app.route("/admin/discounts")
def admin_discounts():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM discounts")
    discounts = cursor.fetchall()
    return render_template("admin_discounts.html", discounts=discounts)

@app.route("/admin/discounts/add", methods=["POST"])
def add_discount():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    discount_id = request.form["discount_id"]
    discount_code = request.form["discount_code"]
    description = request.form["description"]
    discount_percentage = request.form["discount_percentage"]
    query = "INSERT INTO discounts (discount_id, discount_code, description, discount_percentage) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (discount_id, discount_code, description, discount_percentage))
    db.commit()
    flash("Discount added successfully!", "success")
    return redirect(url_for("admin_discounts"))

# ----- Module: Hotel Policies -----

@app.route("/admin/hotel_policies")
def admin_hotel_policies():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    cursor.execute("SELECT * FROM hotel_policies")
    policies = cursor.fetchall()
    return render_template("admin_hotel_policies.html", policies=policies)

@app.route("/admin/hotel_policies/add", methods=["POST"])
def add_policy():
    if not session.get("admin"):
         flash("Please log in as admin", "danger")
         return redirect(url_for("admin_login"))
    policy_id = request.form["policy_id"]
    policy_name = request.form["policy_name"]
    description = request.form["description"]
    query = "INSERT INTO hotel_policies (policy_id, policy_name, description) VALUES (%s, %s, %s)"
    cursor.execute(query, (policy_id, policy_name, description))
    db.commit()
    flash("Hotel policy added successfully!", "success")
    return redirect(url_for("admin_hotel_policies"))

###############################################
#         End of Admin Modules                #
###############################################

if __name__ == "__main__":
    app.run(debug=True)

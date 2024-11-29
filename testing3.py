import streamlit as st
from PIL import Image
import mysql.connector
from mysql.connector import Error
import pandas as pd

st.set_page_config(page_title="Coolgen", page_icon=":snowflake:", layout="wide")

# Create Database Connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="streamlit_db"
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Initialize Database and Tables
def initialize_db():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'Others'
            )
            """)

            # Create tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(255) NOT NULL,
                assigned_to VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'Assigned',
                priority VARCHAR(20) DEFAULT 'Low',
                deadline DATE,
                FOREIGN KEY (assigned_to) REFERENCES users(username)
            )
            """)
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

# Verify Login Credentials
def login(username, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT username, role FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                return True, user  # Return user role
            else:
                return False, "Invalid username or password."
        except Error as e:
            return False, f"Database error: {e}"
        finally:
            cursor.close()
            connection.close()
    return False, "Database connection failed."

# Add User (Admin-Only)
def add_user(admin_username, admin_password, new_username, new_password, role):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Verify if the requester is an Admin
            cursor.execute("SELECT role FROM users WHERE username = %s AND password = %s", (admin_username, admin_password))
            admin = cursor.fetchone()
            if admin and admin[0] == "Admin":
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                               (new_username, new_password, role))
                connection.commit()
                st.toast(f"User {new_username} added successfully as {role}.", icon="☑️")
            else:
                return False, "Only Admins can add users."
        except Error as e:
            st.toast(f"Error adding user: {e}", icon="❌")
        finally:
            cursor.close()
            connection.close()
    return False, ""

# Assign Task to Employee (Manager Only)
def assign_task(manager_username, task_name, description, assigned_to):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Check if the manager is assigning to a valid employee
            cursor.execute("SELECT role FROM users WHERE username = %s", (assigned_to,))
            user = cursor.fetchone()
            if user and user[0] == "Others":  # Only allow assignment to employees
                cursor.execute("""
                INSERT INTO tasks (task_name, description, assigned_to) 
                VALUES (%s, %s, %s)
                """, (task_name, description, assigned_to))
                connection.commit()
                st.success(f"Task '{task_name}' assigned to {assigned_to} successfully.")
            else:
                st.error("Invalid employee username.")
        except Error as e:
            st.error(f"Error assigning task: {e}")
        finally:
            cursor.close()
            connection.close()

# Display Assigned Tasks for Manager
def display_assigned_tasks():
    """Display Assigned Tasks"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT task_name, assigned_to, status FROM tasks WHERE assigned_to = %s", (st.session_state.username,))
            tasks = cursor.fetchall()
            
            if tasks:
                tasks_df = pd.DataFrame(tasks, columns=["Task Name", "Assigned To", "Status"])
                st.dataframe(tasks_df, hide_index=True)
            else:
                st.info("No tasks assigned.")
        except Error as e:
            st.error(f"Error fetching tasks: {e}")
        finally:
            cursor.close()
            connection.close()

# Define functions for sections
def login_page():
    """User Login Page"""
    image = Image.open("images/task.jpeg")

    # Layout: Split into two columns
    col1, col2 = st.columns([2, 3])

    with col1:
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, user_info = login(username, password)
            if success:
                st.session_state.user_logged_in = True
                st.session_state.username = username
                st.session_state.user_role = user_info[1]  # Save user role
                st.success(f"Login successful! Role: {user_info[1]}")
            else:
                st.error(user_info)

def admin_dashboard():
    """Admin Dashboard - Add User"""
    st.subheader("Add a New User")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["Admin", "Manager", "Others"])

    admin_password = st.text_input("Admin Password", type="password")

    col1, col2 = st.columns([2, 8])
    with col1:
        if st.button("Add User"):
            success, message = add_user(
                admin_username=st.session_state.username,
                admin_password=admin_password,
                new_username=new_username,
                new_password=new_password,
                role=role,
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    with col2:
        if st.button("Logout"):
            st.session_state.user_logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.success("Logged out successfully.")

def manager_dashboard():
    """Manager Dashboard - Assign Tasks to Employees"""
    st.subheader("Assign Task to Employee")

    # Fetch list of employees (Others)
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT username FROM users WHERE role = 'Others'")
            employees = cursor.fetchall()
            
            employee_list = [emp[0] for emp in employees]

            if employee_list:
                assigned_to = st.selectbox("Assign Task to Employee", employee_list)
                task_name = st.text_input("Task Name")
                status = st.selectbox("Task Status", ["Assigned", "In Progress", "Completed"])
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                deadline = st.date_input("Deadline")

                if st.button("Assign Task"):
                    if task_name:
                        cursor.execute("""
                            INSERT INTO tasks (task_name, assigned_to, status, priority, deadline)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (task_name, assigned_to, status, priority, deadline))
                        connection.commit()
                        st.success(f"Task '{task_name}' assigned to {assigned_to} with {priority} priority and deadline {deadline}!")
                    else:
                        st.error("Please enter a valid task name.")
            else:
                st.warning("No employees (Others) available to assign tasks.")
        except Error as e:
            st.error(f"Error fetching employees: {e}")
        finally:
            cursor.close()
            connection.close()

    # Add Logout Button
    if st.button("Logout"):
        st.session_state.user_logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.success("Logged out successfully.")


def dashboard_page():
    """General Dashboard for all users"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Manager'")
            managers_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Others'")
            others_count = cursor.fetchone()[0]

            col1, col2 = st.columns([2, 9])
            with col1:
                st.metric(label="Managers", value=managers_count, help="No. of Managers")
            with col2:
                st.metric(label="Others", value=others_count, help="No. of Employees other than Manager")

        except Error as e:
            st.error(f"Error fetching user counts: {e}")
        finally:
            cursor.close()
            connection.close()

    # Button to display users by category
    if st.button("Display All Users."):
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT username, role FROM users WHERE role != 'Admin'")
                users = cursor.fetchall()
                
                if users:
                    users_df = pd.DataFrame(users, columns=["Username", "Role"])
                    st.dataframe(users_df, hide_index=True)
                else:
                    st.info("No users found.")
            except Error as e:
                st.error(f"Error fetching users: {e}")
            finally:
                cursor.close()
                connection.close()

    # Logout button
    if st.button("Logout"):
        st.session_state.user_logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.success("Logged out successfully.")

# Employee Dashboard - View Assigned Tasks
def employee_dashboard():
    """Employee Dashboard - View Assigned Tasks"""
    st.subheader("Your Assigned Tasks")

    # Fetch assigned tasks for the logged-in employee
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT task_name, status, priority, deadline FROM tasks WHERE assigned_to = %s", (st.session_state.username,))
            tasks = cursor.fetchall()
            
            if tasks:
                tasks_df = pd.DataFrame(tasks, columns=["Task Name", "Status","Priority","Deadline"])
                st.dataframe(tasks_df, hide_index=True)
            else:
                st.info("You have no assigned tasks.")
        except Error as e:
            st.error(f"Error fetching tasks: {e}")
        finally:
            cursor.close()
            connection.close()
        # Logout button
    if st.button("Logout"):
        st.session_state.user_logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.success("Logged out successfully.")


# Main app logic
def main():
    st.markdown(
        """
        <h1 style="text-align: center;"><strong>Task Management Web App</strong></h1>
        """, unsafe_allow_html=True
    )

    # Initialize database on app start
    initialize_db()
    
    # Initialize session state variables
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None

    # Login page or Dashboard
    if not st.session_state.user_logged_in:
        login_page()
    else:
        # Show appropriate dashboard based on user role
        if st.session_state.user_role == "Manager":
            manager_dashboard()
        elif st.session_state.user_role == "Admin":
            admin_dashboard()
        elif st.session_state.user_role == "Others":
            employee_dashboard()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()

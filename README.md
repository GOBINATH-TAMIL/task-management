# Task Management Web Application

## Overview

Hi,  
This is a **Task Management Web Application**, created using Python programming language.  
In this application, I have implemented three user roles with specific functionalities: **Admin**, **Manager**, and **Developer**.  

- The **Admin** has the authority to add new users to the application. While adding a user, the Admin assigns a role to them, either as a **Manager** or a **Developer**.
- The **Manager** can create and assign tasks to Developers.
- The **Developer** can view the tasks assigned to them and update their status.

Before using this application, users must log in through the **Login Page**, which serves as an authentication mechanism. This ensures that only authorized users can access the application and perform tasks based on their assigned roles.  
The authentication system adds a layer of security, enabling role-specific access for **Admins**, **Managers**, and **Developers**. This role-based structure ensures proper task delegation and management within the application.

## Tools and Technologies Used

- **Python (Streamlit)**: For application development and the front-end interface.
- **VS Code**: As the primary code editor.
- **XAMPP MySQL**: For database management.

## How to Run This File

### 1) Download and Prepare the Project Files

- Save the project files to your system.
- Create a folder named **Task_management** and move all the files into this folder.
- Note: The file `config.toml` is hidden and located in the `.streamlit` folder. Follow these steps:
  - Create a subfolder named `.streamlit` inside the **Task_management** folder.
  - Move the `config.toml` file into the `.streamlit` folder.

Your folder structure should now look like this:

Task_management/ │-- testing3.py │-- requirements.txt │-- .streamlit/ │ └── config.toml │-- images/

### 2) Create and Activate a Virtual Environment

- Open a terminal/command prompt and navigate to the **Task_management** folder.

- Create a virtual environment using the following command:
- 
   "python -m venv venv"

- Activate the virtual environment using the following command:

  "venv\Scripts\activate"

  
### 3) Install Required Libraries

- Inside the virtual environment, install the necessary libraries using `requirements.txt`:

 "pip install -r requirements.txt"


### 4) Create Database

Before running the application, ensure that your MySQL database server is running. The MySQL server should have a database named **streamlit_db**, as specified in the code.

### 5) Run the Application

- Run the **testing3.py** file using the following command:

"streamlit run testing3.py"


This will launch the web application in your default browser.

## Conclusion

This application provides a simple, role-based task management system, with functionalities for Admin, Manager, and Developer users. The use of Streamlit makes the app interactive and easy to deploy, while XAMPP and MySQL handle database management for storing user and task data.

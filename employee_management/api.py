from __future__ import unicode_literals
import frappe
from frappe import auth
from frappe.utils import now
from frappe import _
from frappe.utils.password import check_password
import json

@frappe.whitelist(allow_guest=True)
def login(username, password):
    try:
        # Authenticate the user
        frappe.local.login_manager.authenticate(username, password)
        frappe.local.login_manager.post_login()

        # Return session info
        return {
            "message": _("Logged in successfully"),
            "session_id": frappe.session.sid,
            "user": frappe.session.user
        }
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.throw(_("Invalid username or password"), frappe.AuthenticationError)


# @frappe.whitelist(allow_guest=True)
# def login(username, password):
#     try:
#         # Fetch user details from User Accounts
#         user_account = frappe.db.get_value(
#             "User Accounts",
#             {"email_address": username},
#             ["email_address", "password"],
#             as_dict=True
#         )
        
#         # Check if user exists
#         if not user_account:
#             frappe.throw(_("Incorrect User or Password"), frappe.AuthenticationError)
        
#         # Verify password (hashed or plain)
#         # if not check_password(user_account["password"], password):
#         #     frappe.throw(_("Incorrect User or Password"), frappe.AuthenticationError)
        
#         # Simulate login
#         frappe.local.login_manager.user = username
#         frappe.local.login_manager.post_login()
        
#         # Return session info
#         return {
#             "message": _("Logged in successfully"),
#             "session_id": frappe.session.sid,
#             "user": frappe.local.login_manager.user
#         }

#     except frappe.AuthenticationError as e:
#         frappe.clear_messages()
#         frappe.throw(str(e), frappe.AuthenticationError)
#     except Exception as e:
#         frappe.log_error(message=str(e), title="Custom Login Error")
#         frappe.throw(_("An unexpected error occurred during login."))



#########################################   Company       ##########################################

@frappe.whitelist()
def get_company(company_id=None):
    if company_id:
        # Fetch specific company
        company = frappe.get_doc("Company Emp", company_id)
        return company.as_dict()
    else:
        # Fetch all companies
        companies = frappe.get_all("Company Emp", fields=["name", "number_of_departments", "company_name","number_of_employees","number_of_projects"])
        return companies

#########################################   Department       ##########################################

@frappe.whitelist()
def get_department(department_id=None):
    if department_id:
        # Fetch specific department
        department = frappe.get_doc("Department Emp", department_id)
        return department.as_dict()
    else:
        # Fetch all departments
        departments = frappe.get_all("Department Emp", fields=["name", "number_of_projects", "number_of_employees","company","department_name"])
        return departments



#########################################   Employee       ##########################################
@frappe.whitelist()
def create_employee(**kwargs):
    # Validate input data
    required_fields = ["email_address", "department", "mobile_number", "address", "designation", "employee_status", "employee_name", "company"]
    for field in required_fields:
        if not kwargs.get(field):
            frappe.throw(f"Field {field} is required")

    if frappe.db.exists("Employee Emp", {"email_address": kwargs.get("email_address")}):
        frappe.throw(f"An employee with email address {kwargs.get('email_address')} already exists.")

    if not frappe.db.exists("Company Emp", kwargs.get("company")):
        frappe.throw(f"Company '{kwargs.get('company')}' does not exist in Company.")

    if not frappe.db.exists("Department Emp", kwargs.get("department")):
        frappe.throw(f"Department '{kwargs.get('department')}' does not exist in Department.")

    employee = frappe.get_doc({
        "doctype": "Employee Emp",
        "email_address": kwargs.get("email_address"),
        "department": kwargs.get("department"),
        "mobile_number": kwargs.get("mobile_number"),
        "address": kwargs.get("address"),
        "designation": kwargs.get("designation"),
        "employee_status": kwargs.get("employee_status"),
        "employee_name": kwargs.get("employee_name"),
        "company": kwargs.get("company"),
    })
    
    employee.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Employee created successfully", "employee_id": employee.name}

@frappe.whitelist()
def get_employee(employee_id=None):
    if employee_id:
        # Fetch specific employee
        employee = frappe.get_doc("Employee Emp", employee_id)
        return employee.as_dict()
    else:
        # Fetch all employees
        employees = frappe.get_all("Employee Emp", fields=["email_address", "department", "mobile_number", "address", "designation", "employee_status", "employee_name", "company"])
        return employees


@frappe.whitelist()
def update_employee(employee_id, **kwargs):
    if not employee_id:
        frappe.throw("Employee ID is required")

    employee = frappe.get_doc("Employee Emp", employee_id)
    for key, value in kwargs.items():
        setattr(employee, key, value)
    employee.save()
    frappe.db.commit()
 
    return {"message": "Employee updated successfully"}


@frappe.whitelist()
def delete_employee(employee_id):
    if not employee_id:
        frappe.throw("Employee ID is required")

    frappe.delete_doc("Employee Emp", employee_id, ignore_permissions=True)
    frappe.db.commit()
 
    return {"message": "Employee deleted successfully"}



#########################################   Project       ##########################################


@frappe.whitelist()
def create_project(**kwargs):
    required_fields = ["company", "project_name", "department", "start_date", "end_date", "assigned_employees"]
    for field in required_fields:
        if not kwargs.get(field):
            frappe.throw(f"Field {field} is required")

    if not frappe.db.exists("Company Emp", kwargs.get("company")):
        frappe.throw(f"Company '{kwargs.get('company')}' does not exist in Company.")

    if not frappe.db.exists("Department Emp", kwargs.get("department")):
        frappe.throw(f"Department '{kwargs.get('department')}' does not exist in Department.")

    try:
        assigned_employees = json.loads(kwargs.get("assigned_employees"))
    except Exception as e:
        frappe.throw(f"Invalid assigned_employees format. Error: {str(e)}")

    if not assigned_employees:
        frappe.throw("Assigned employees are required.")

    for employee in assigned_employees:
        if not frappe.db.exists("Employee Emp", employee.get("employee")):
            frappe.throw(f"Employee '{employee.get('employee')}' does not exist in Employee.")

    project = frappe.get_doc({
        "doctype": "Project Emp",
        "company": kwargs.get("company"),
        "project_name": kwargs.get("project_name"),
        "department": kwargs.get("department"),
        "start_date": kwargs.get("start_date"),
        "end_date": kwargs.get("end_date"),
    })
    
    for employee in assigned_employees:
        project.append("assigned_employees", {
            "employee": employee.get("employee")
        })

    project.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Project created successfully", "project_id": project.name}
@frappe.whitelist()
def get_project(project_id=None):
    if project_id:
        # Fetch specific project
        project = frappe.get_doc("Project Emp", project_id)
        return project.as_dict()
    else:
        # Fetch all project
        projects = frappe.get_all("Project Emp", fields=["company", "project_name", "department","description","start_date","end_date","assigned_employees"])
        return projects


@frappe.whitelist()
def update_project(project_id, **kwargs):
    if not project_id:
        frappe.throw("Project ID is required")

    project = frappe.get_doc("Project Emp", project_id)
    for key, value in kwargs.items():
        setattr(project, key, value)
    project.save()
    frappe.db.commit()

    return {"message": "Project updated successfully"}


@frappe.whitelist()
def delete_project(project_id):
    if not project_id:
        frappe.throw("Project ID is required")

    frappe.delete_doc("Project Emp", project_id, ignore_permissions=True)
    return {"message": "Project deleted successfully"}

# Copyright (c) 2024, hazemsharaf56@gmail.com and contributors
# For license information, please see license.txt
import frappe
from frappe.exceptions import ValidationError
from frappe.model.document import Document
from datetime import datetime, date  
import re
from datetime import datetime
ALLOWED_TRANSITIONS = {
    "Application Received": ["Interview Scheduled", "Not Accepted"],
    "Interview Scheduled": ["Hired", "Not Accepted"],
    "Not Accepted": ["Interview Scheduled"],
    "Hired": [] 
}


class EmployeeEmp(Document):


    def before_validate(self):
        validate_employee_status(self)
        
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if self.email_address and not re.match(email_regex, self.email_address):
            frappe.throw("Invalid email address format.")
        
        phone_regex = r'^[0-9]{10}$'
        if self.mobile_number and not re.match(phone_regex, self.mobile_number):
            frappe.throw("Invalid phone number format.")
        
        if self.hired_on and self.employee_status == "Hired":
            # Ensure hired_on is a datetime object if it is not already
            if isinstance(self.hired_on, str):
                hired_on_date = datetime.strptime(self.hired_on, "%Y-%m-%d")
            else:
                # If it's a date, convert it to datetime
                if isinstance(self.hired_on, date):  # Use 'date' from datetime module
                    hired_on_date = datetime.combine(self.hired_on, datetime.min.time())
                else:
                    hired_on_date = self.hired_on  # Already a datetime object
            
            today = datetime.today()
            days_with_company = (today - hired_on_date).days
            self.days_with_company = days_with_company
        
        if self.hired_on:
            try:
                # Ensure hired_on is a datetime object if it is not already
                if isinstance(self.hired_on, str):
                    hired_date = datetime.strptime(self.hired_on, "%Y-%m-%d")
                else:
                    # If it's a date, convert it to datetime
                    if isinstance(self.hired_on, date):  # Use 'date' from datetime module
                        hired_date = datetime.combine(self.hired_on, datetime.min.time())
                    else:
                        hired_date = self.hired_on  # Already a datetime object
                
                today = datetime.today()
                self.days_employed = (today - hired_date).days
            except ValueError:
                frappe.throw("Invalid date format for 'Hired On'. Expected format: YYYY-MM-DD.")

        company = self.company
        department = self.department
        update_department_counts(department)
        update_company_counts(company)
        department_company = frappe.db.get_value('Department Emp', department, 'company')
        if department_company != company:
            frappe.throw(f"Department {department} does not belong to the selected company.")

    def on_delete(self):
        related_records = frappe.get_all('Project Emp', filters={'assigned_employee': self.name})
        if related_records:
            frappe.throw("Cannot delete this employee, as they are assigned to ongoing projects.")



def validate_employee_status(doc, method=None):
    previous_status = frappe.db.get_value("Employee Emp", doc.name, "employee_status")
    new_status = doc.employee_status

    if previous_status == new_status:
        return

    if previous_status and new_status not in ALLOWED_TRANSITIONS.get(previous_status, []):
        frappe.throw(
            f"Invalid status transition from '{previous_status}' to '{new_status}'."
        )

@frappe.whitelist()
def update_company_counts(company_id):
    """
    Updates the counts of employees for a given company.
    """
    company = frappe.get_doc("Company Emp", company_id)
        
    employee_count = frappe.db.count("Employee Emp", filters={"company": company_id})
    
    company.number_of_employees = employee_count
    company.save()

@frappe.whitelist()
def update_department_counts(department_id):
    """
    Updates the counts of employees for a given department.
    """
    department = frappe.get_doc("Department Emp", department_id)
    
    employee_count = frappe.db.count("Employee Emp", filters={"department": department_id})
    

    department.number_of_employees = employee_count
    department.save()



@frappe.whitelist()
def change_employee_status(employee_id, new_status):
    doc = frappe.get_doc("Employee Emp", employee_id)
    doc.employee_status = new_status
    doc.save()
    frappe.db.commit()
    return f"Employee status updated to {new_status}"

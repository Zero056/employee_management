# Copyright (c) 2024, hazemsharaf56@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectEmp(Document):
    def validate(self):
        update_company_counts(self.company)
        update_department_counts(self.department)
        for row in self.assigned_employees:
            update_project_count(row.employee,self.name)

@frappe.whitelist()
def update_project_count(employee_id, project_id):
    """
    Updates the number of assigned projects for an employee.
    """
    employee = frappe.get_doc("Employee Emp", employee_id)
    
    project_count = frappe.db.count("Assigned Employees", filters={"employee": employee_id, "parent": project_id})

    employee.number_of_assigned_projects = project_count
    
    employee.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.msgprint(employee.number_of_assigned_projects)


@frappe.whitelist()
def update_company_counts(company_id):
    """
    Updates the counts of projects for a given company.
    """
    company = frappe.get_doc("Company Emp", company_id)
        
    project_count = frappe.db.count("Project Emp", filters={"company": company_id})

    company.number_of_projects = project_count
    company.save()
    frappe.db.commit()


@frappe.whitelist()
def update_department_counts(department_id):
    """
    Updates the counts of Project for a given department.
    """
    department = frappe.get_doc("Department Emp", department_id)
    
    project_count = frappe.db.count("Project Emp", filters={"department": department_id})
    

    department.number_of_projects = project_count
    department.save()
    frappe.db.commit()

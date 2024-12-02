# Copyright (c) 2024, hazemsharaf56@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DepartmentEmp(Document):
	def before_validate(self):
		update_company_counts(self.company)

@frappe.whitelist()
def update_company_counts(company_id):
    """
    Updates the counts of departments for a given company.
    """
    company = frappe.get_doc("Company Emp", company_id)
    
    department_count = frappe.db.count("Department Emp", filters={"company": company_id})
    
    company.number_of_departments = department_count
    company.save()
    frappe.db.commit()


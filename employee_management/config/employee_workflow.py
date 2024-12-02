class EmployeeOnboarding(Document):
    def validate(self):
        self.validate_onboarding_status()

    def validate_onboarding_status(self):
        # Implement the allowed transitions
        if self.onboarding_status == "Application Received":
            if self.previous_onboarding_status == "Interview Scheduled" or self.previous_onboarding_status == "Not Accepted":
                frappe.throw("Invalid transition: Cannot move from Interview Scheduled or Not Accepted directly to Application Received.")

        if self.onboarding_status == "Interview Scheduled":
            if self.previous_onboarding_status not in ["Application Received"]:
                frappe.throw("Invalid transition: Can only move to Interview Scheduled from Application Received.")

        if self.onboarding_status == "Hired":
            if self.previous_onboarding_status != "Interview Scheduled":
                frappe.throw("Invalid transition: Can only move to Hired from Interview Scheduled.")

        if self.onboarding_status == "Not Accepted":
            if self.previous_onboarding_status != "Application Received" and self.previous_onboarding_status != "Interview Scheduled":
                frappe.throw("Invalid transition: Can only move to Not Accepted from Application Received or Interview Scheduled.")

        if self.onboarding_status == "Not Accepted":
            if self.previous_onboarding_status == "Not Accepted":
                frappe.throw("Invalid transition: Cannot transition back to Interview Scheduled once Not Accepted.")

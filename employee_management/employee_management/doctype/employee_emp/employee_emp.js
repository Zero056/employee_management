// Copyright (c) 2024, hazemsharaf56@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Emp", {
    refresh: function (frm) {
        frm.add_custom_button("Action", () => {
            show_action_dialog(frm);
        });
        if (frm.doc.employee_status == "Hired") {
            frm.set_df_property('hired_on', 'reqd', 1); 
            frm.set_df_property('hired_on', 'hidden', 0);
            //////////////////////
            frm.set_df_property('days_employed', 'hidden', 0);
            //////////////////////
            frm.set_df_property('number_of_assigned_projects', 'hidden', 0);
            //////////////////////
        } else {
            frm.set_df_property('hired_on', 'reqd', 0);  
            frm.set_df_property('hired_on', 'hidden', 1);
            ///////////////////////
            frm.set_df_property('days_employed', 'hidden', 1);
            //////////////////////
            frm.set_df_property('number_of_assigned_projects', 'hidden', 0);
            ///////////////////////
        }
    }

});

// Function to display action dialog
function show_action_dialog(frm) {
    const actions = get_available_actions(frm.doc.employee_status);

    if (!actions.length) {
        frappe.msgprint("No actions available for the current status.");
        return;
    }

    // Create a dialog to show available actions
    const dialog = new frappe.ui.Dialog({
        title: "Select Action",
        fields: [
            {
                label: "Action",
                fieldname: "selected_action",
                fieldtype: "Select",
                options: actions.map(action => action.label),
                reqd: 1
            }
        ],
        primary_action_label: "Submit",
        primary_action(values) {
            const selected_action = actions.find(action => action.label === values.selected_action);
            if (selected_action) {
                update_employee_status(frm, selected_action.new_status);
            }
            dialog.hide();
        }
    });

    dialog.show();
}

// Helper function to get available actions for the current status
function get_available_actions(current_status) {
    const action_map = {
        "Application Received": [
            { label: "Schedule Interview", new_status: "Interview Scheduled" },
            { label: "Reject", new_status: "Not Accepted" }
        ],
        "Interview Scheduled": [
            { label: "Hire", new_status: "Hired" },
            { label: "Reject", new_status: "Not Accepted" }
        ],
        "Not Accepted": [
            { label: "Reconsider", new_status: "Interview Scheduled" }
        ]
    };

    return action_map[current_status] || [];
}

// Helper function to update employee status
function update_employee_status(frm, new_status) {
    frappe.call({
        method: "employee_management.employee_management.doctype.employee_emp.employee_emp.change_employee_status", 
        args: {
            employee_id: frm.doc.name,
            new_status: new_status
        },
        callback: function (response) {
            frappe.msgprint(response.message || `Status changed to ${new_status}`);
            frm.reload_doc();
        }
    });
}

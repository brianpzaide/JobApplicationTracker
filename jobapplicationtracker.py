from tkinter import *
import tkinter as tk
from tkinter import ttk, scrolledtext
import ttkbootstrap as tb
import db

instruction_text = """Click a row in the table above to view job application notes. Right-click to update or add new notes. When you right-click a row, the form below will automatically fill with the corresponding values."""


def row_left_click(event):
    """Fetches the notes for the job application corresponding to the row just clicked.

    Args:
        event: ttk event
    """
    # fetch the item selected
    item_id = trv.identify_row(event.y)
    item_data = trv.item(item_id, 'values')
    # check to make sure that a row has been clicked
    if len(item_data) > 0:
        # fetch the notes for that specific job application
        notes = db.fetch_notes(int(item_data[0]))
        notes_display = f"\n{'='*52}\n".join(notes)
        # populate the textbox in the notes_frame with the just fetched notes
        # set the state to 'enabled'
        notesbox['state'] = NORMAL
        # remove all the previoustext
        notesbox.delete("1.0", END)
        # insert the new text
        notesbox.insert(index=END, chars=notes_display)
        # disable the textbox
        notesbox['state'] = DISABLED
    

def row_right_click(event):
    """Automatically populates the Add/Update form fields with the values corresponding to the row you just right-clicked.

    Args:
        event: ttk event
    """
    # fetch the details of that specific job application
    item_id = trv.identify_row(event.y)
    item_data = trv.item(item_id, 'values')
    
    # check to make sure that a row has been clicked
    if len(item_data) > 0:
        print('row_right_click', item_data)
        # clear the form
        clear_form()
        # populate the form fields with the just fetched job apllication details
        id_entry.insert(END, item_data[0])
        company_name_entry.insert(END, item_data[1])
        position_entry.insert(END, item_data[2])
        status_var.set(item_data[3])
        date_deadline, time_deadline = tuple(item_data[4].split())
        next_deadline.entry.delete("0", END)
        temp = date_deadline.split("-")
        date_deadline = f"{temp[1]}/{temp[2]}/{temp[0]}"
        next_deadline.entry.insert("0", date_deadline)
        time_entry.insert(END, time_deadline)

    
    

def clear_form():
    """Resets all form fields, clearing any entered data in the Add/Update form.
    """
    id_entry.delete(0, tk.END)
    company_name_entry.delete(0, END)
    position_entry.delete(0, END)
    time_entry.delete(0, END)
    status_var.set("status 0")
    new_note_textbox.delete("1.0", END)
    next_deadline.selection_clear() 
    
def add_job_application():
    """Collects information entered in the Add/Update form and saves it as a new job application in the database.
    """
    # get the values from the fields "company", "position", "status", "next_deadline", "Time"
    new_company_name = company_name_entry.get()
    new_job_position = position_entry.get()
    new_job_status = status_var.get()
    new_job_date = next_deadline.entry.get()
    new_job_time = time_entry.get()
    if new_company_name.strip() and new_job_position.strip() and new_job_status.strip() and new_job_date.strip() and new_job_time.strip():
        temp = new_job_date.split("/")
        new_job_date = f"{temp[2]}-{temp[0].zfill(2)}-{temp[1].zfill(2)}"
        # insert the new job application into the database
        db.add_job(new_company_name, new_job_position, new_job_status, new_job_date, new_job_time)
        # call refresh_table_view
        refresh_table_view()
        # clear the form
        clear_form()

def update_job_application():
    """Updates the selected job application. When a row in the table is right-clicked, the fields of the Add/Update form are automatically populated with the corresponding values.
This function collects information from the Add/Update form and updates the corresponding job application in the database. It retrieves only the 'id', 'status', 'next_deadline', and 'time' fields, leaving the 'company name' and 'position' unchanged, as modifying them has no effect.
This function is specifically designed to update the status and 'next_deadline' of the job application.
    """
    # get the values from the fields "id" "status", "next_deadline", "Time"
    jid = id_entry.get()
    new_status = status_var.get()
    next_date = next_deadline.entry.get()
    next_time = time_entry.get()
    if jid.strip():
        jid = int(jid)
        if new_status and next_date.strip() and next_time.strip():
            temp = next_date.split("/")
            next_date = f"{temp[2]}-{temp[0].zfill(2)}-{temp[1].zfill(2)}"
            # insert the new job application into the database
            db.update_job_application(jid, new_status, next_date, next_time)
            # call refresh_table_view
            refresh_table_view()
            # clear the form
            clear_form()

def add_note():
    """Adds a new note for the selected job application into the database. Ensure the 'id' field in the Add/Update form is populated; otherwise, it has no effect (no operation). Right-clicking on the row corresponding to the job application automatically populates the required field.
    """
    # get the values from the fields "id", "note"
    _id = id_entry.get()
    if _id.strip():
        _id = int(_id)
        _new_note = new_note_textbox.get("1.0", tk.END)
        # add new note to the database
        db.add_note(job_application_id=_id, new_note=_new_note)
        # update the textbox in the note_frame
        notesbox['state'] = NORMAL
        prev = notesbox.get("1.0", tk.END)
        notesbox.delete("1.0", tk.END)
        notes_display = _new_note + f"\n{'='*52}\n" + prev
        notesbox.insert(index="1.0", chars=notes_display)
        notesbox['state'] = DISABLED
        # clear the form
        clear_form()
    

def refresh_table_view():
    """Clears and refreshes the table with the most recent data from the database.
    """
    # clear the tree view
    trv.delete(*trv.get_children())
    # call filter_job_applications to fetch the filtered job applications
    _jas = filter_job_applications()
    # update the tree view using the recently fetched data
    for _ja in _jas:
        trv.insert(parent='', index=END, values=_ja)
    

def filter_job_applications():
    """Fetches all job applications from the database, applying filters based on company names, positions, status, and alseo date(useful for finding applications due next week or next month etc).  

    Returns:
        _type_: _description_
    """
    # get the values from the fields "company_name_menu", "position_menu", "status_menu", "from_date", "to_date"
    _companies = [item for item, var in company_name_vars.items() if var.get()]
    _positions = [item for item, var in position_vars.items() if var.get()]
    _statusses = [item for item, var in status_vars.items() if var.get()]
    _from, _through = "", ""
    from_state =  str(from_date.entry['state']).strip()
    through_state = str(to_date.entry['state']).strip()

    if from_state == 'normal':
        temp = from_date.entry.get().split("/")
        _from = f"{temp[2]}-{temp[0]}-{temp[1]}"
        from_date.set_state_disabled()
    if through_state == 'normal':
        temp = to_date.entry.get().split("/")
        _through = f"{temp[2]}-{temp[0]}-{temp[1]}"
        to_date.set_state_disabled()

    # call db.filter_job_applications to get the filtered results
    return db.filter_job_applications(_companies, _positions, _statusses, _from.strip(), _through.strip())


root = tb.Window(themename="darkly")
root.geometry("1100x670")
root.resizable(False, False)


class CustomDateEntry(tb.DateEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry["state"] = "readonly"

    def _on_date_ask(self):
        self.entry["state"] = "normal"
        super()._on_date_ask()

    def set_state_disabled(self):
        self.entry["state"] = "readonly"

####################### building the search frame that contains the search widgets ########################
search_frame = LabelFrame(root, text="Search")
search_frame.pack(fill="x", padx=10, pady=10)

companies = db.fetch_companies()
company_name_menu = tb.Menubutton(search_frame, bootstyle="warning", text="Select Company", width=15)
company_name_menu.grid(row=0, column=0, padx=10, columnspan=2)
company_name_menu_inside = tb.Menu(company_name_menu)
company_name_vars = {}
for company in companies:
    var = tk.BooleanVar()
    company_name_vars[company] = var
    company_name_menu_inside.add_checkbutton(label=company, variable=var)
company_name_menu['menu'] = company_name_menu_inside

# populating the position_menu with all the unique positions currently in the database
positions = db.fetch_positions()
position_menu = tb.Menubutton(search_frame, bootstyle="warning", text="Select Position", width=15)
position_menu.grid(row=0, column=2, padx=10, columnspan=2)
position_menu_inside = tb.Menu(position_menu)
position_vars = {}
for pos in positions:
    var = tk.BooleanVar()
    position_vars[pos] = var
    position_menu_inside.add_checkbutton(label=pos, variable=var)
position_menu['menu'] = position_menu_inside

# populating the status_menus with the 'statusses'
statusses = ["ready to apply", "applied", "interview scheduled", "rejected", "ghosted", "offered", "signed", "archived"]
status_menu = tb.Menubutton(search_frame, bootstyle="warning", text="Select Status", width=15)
status_menu.grid(row=0, column=4, padx=10, columnspan=2)
status_menu_inside = tb.Menu(status_menu)
status_vars = {}
for _status in statusses:
    var = tk.BooleanVar()
    status_vars[_status] = var
    status_menu_inside.add_checkbutton(label=_status, variable=var)
status_menu['menu'] = status_menu_inside

from_date = CustomDateEntry(search_frame, bootstyle="warning", width=15)
from_date.grid(row=0, column=6, columnspan=2, padx=10)

to_date = CustomDateEntry(search_frame, bootstyle="warning", width=15)
to_date.grid(row=0, column=8, columnspan=2, padx=10)

filter_btn = tb.Button(search_frame, text="Filter / Refresh", bootstyle="success", command=refresh_table_view)
filter_btn.grid(row=0, sticky="e", column=12, padx=80)

from_date_label = tb.Label(search_frame, text="(from)", width=6)
from_date_label.grid(row=1, column=6, padx=10, columnspan=2)

to_date_label = tb.Label(search_frame, text="(through)", width=10)
to_date_label.grid(row=1, column=8, columnspan=2, padx=10)

###################################################################################################################################################

################################### building the table_frame that contains the Table(Treeview) and the notes section #################################################
main_frame = LabelFrame(root, text="Table and Notes")
main_frame.pack(fill="both", expand="yes",  padx=10, pady=10)

table_frame = LabelFrame(main_frame, width=500, text="Job Applications")
table_frame.pack(fill="both", expand="yes",  padx=10, pady=10, side=LEFT)
trv = ttk.Treeview(table_frame, columns=(1,2,3,4,5), show="headings")
trv.pack(fill="both", expand="yes")
trv['columns'] = ("id", "Company Name", "Position", "Status", "Next Deadline")
trv.column("#0", width=0, stretch=NO)
trv.column("id", width=120, minwidth=25, anchor=CENTER)
trv.column("Company Name", width=120, minwidth=25, anchor=CENTER)
trv.column("Position", width=120, minwidth=25, anchor=CENTER)
trv.column("Status", width=120, minwidth=25, anchor=CENTER)
trv.column("Next Deadline", width=120, minwidth=25, anchor=CENTER)
trv.heading("#0", text="")
trv.heading("id", text="id")
trv.heading("Company Name", text="Company Name")
trv.heading("Position", text="Position")
trv.heading("Status", text="Status")
trv.heading("Next Deadline", text="Next Deadline")
trv.bind('<ButtonRelease-1>', row_left_click)
trv.bind('<ButtonRelease-3>', row_right_click)

# populating the table
job_applications = db.filter_job_applications()

for ja in job_applications:
    trv.insert(parent='', index=END, values=ja)

notes_frame = LabelFrame(main_frame, width=450, text="Job Application Notes")
notes_frame.pack(fill="both", expand="yes",  padx=10, pady=10, side=RIGHT)
notesbox = Text(notes_frame,height=0, width=400, wrap="word")
notesbox.pack(side="top", fill="both", expand="yes")
notesbox['state'] = DISABLED
#######################################################################################################################################################

############################## building add update frame that contains form to add new or update existing job applications ##################################### 
add_update_frame = LabelFrame(root, text="Add/Update")
add_update_frame.pack(fill="x", padx=10)

frame_1 = Frame(add_update_frame)
frame_1.pack(side=LEFT)

instruction_frame = Frame(frame_1)
instruction_frame.pack(side=TOP)
instructionbox = Text(instruction_frame, height=2, width=70, wrap="word")
instructionbox.pack()
instructionbox.insert(index=END, chars=instruction_text)
instructionbox['state'] = DISABLED

input_frame = Frame(frame_1)
input_frame.pack(pady=10)

id_entry = tb.Entry(input_frame, width=20)
id_entry.grid(row=1, column=0, padx=10)
id_label = tb.Label(input_frame, width=15, text="             Id")
id_label.grid(row=0, column=0, padx=10)

company_name_entry = tb.Entry(input_frame, width=20)
company_name_entry.grid(row=1, column=1, padx=10)
company_name_label = tb.Label(input_frame, width=15, text="Company Name")
company_name_label.grid(row=0, column=1, padx=10)

position_entry = tb.Entry(input_frame, width=20)
position_entry.grid(row=1, column=2, padx=10)
position_label = tb.Label(input_frame, width=15, text="      Position")
position_label.grid(row=0, column=2, padx=10)

status_menu = tb.Menubutton(input_frame, bootstyle="warning", width=15, text="Select Status")
status_menu.grid(row=3, column=0, padx=10)
status_label = tb.Label(input_frame, width=15, text="        Status")
status_label.grid(row=2, column=0, padx=10)
status_menu_inside = tb.Menu(status_menu)
status_var = StringVar()
for _status in statusses:
    status_menu_inside.add_radiobutton(label=_status, variable=status_var)
status_menu['menu'] = status_menu_inside

next_deadline = tb.DateEntry(input_frame, bootstyle="warning", width=15)
next_deadline.grid(row=3, column=1, padx=10)
next_deadline_label = tb.Label(input_frame, width=15, text="  Next Deadline")
next_deadline_label.grid(row=2, column=1, padx=10)

time_entry = tb.Entry(input_frame, width=20)
time_entry.grid(row=3, column=2, padx=10)
time_label = tb.Label(input_frame, width=15, text="Time(HH:MM)")
time_label.grid(row=2, column=2, padx=10)


frame_2 = Frame(add_update_frame)
frame_2.pack(side=LEFT, padx=10)

new_note_frame = Frame(frame_2)
new_note_frame.pack()
new_note_label = tb.Label(new_note_frame, text="New Note", width=15)
new_note_label.grid(row=1, column=0, padx=50)
new_note_textbox = scrolledtext.ScrolledText(new_note_frame, height=10, width=75,wrap="word")
new_note_textbox.grid(row=2, column=0)


control_frame = Frame(add_update_frame)
control_frame.pack(side=LEFT)

add_btn = tb.Button(control_frame, text="Add", bootstyle="warning", width=10, command=add_job_application)
add_btn.grid(row=0, column=0, pady=10)

update_btn = tb.Button(control_frame, text="Update", bootstyle="warning", width=10, command=update_job_application)
update_btn.grid(row=1, column=0, pady=10)

add_note_btn = tb.Button(control_frame, text="Add Note", bootstyle="warning", width=10, command=add_note)
add_note_btn.grid(row=2, column=0, pady=10)

clear_btn = tb.Button(control_frame, text="Clear Form", bootstyle="warning", width=10, command=clear_form)
clear_btn.grid(row=3, column=0, pady=10)

root.mainloop()

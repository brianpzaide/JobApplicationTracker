import sqlite3
import random
from collections import namedtuple


from typing import List

JobApplication = namedtuple("JobApplication", "id company position status next_deadline")

lorem_ipsum = "res et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque e"

companies = ["apple", "google", "netflix", "meta", "amazon", "adobe", "ibm", "redhat", "reddit", "vmware"]

positions = ["swe", "software developer", "sdet", "technical writer", "devops", "sre", "infra"]

status = ["ready to apply", "applied", "ghosted", "interview scheduled", "rejected", "offered", "signed", "archived"]

one_month_past_dates = [
    f"2024-02-{str(i).zfill(2)} 11:00" for i in range(30)
]

current_month_dates = [
    f"2024-03-{str(i).zfill(2)} 11:00" for i in range(32)
]

one_month_future_dates = [
    f"2024-04-{str(i).zfill(2)} 11:00" for i in range(31)
]

def init_db():
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        cur.executescript(f.read())
    conn.commit()
    conn.close()

j_insert_query = "Insert into job_applications (company, position, status, next_deadline) values (?, ?, ?, ?)"
notes_insert_query = "Insert into notes (job_application_id, note) values (?, ?)"
job_application_fetch_query = "select * from job_applications where id = ?"
notes_fetch_query = "Select note from notes where job_application_id = ?"
job_update_query = "Update job_applications set status= ?, next_deadline = ? where id = ?"

def generate_data():
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    past_positions = random.randint(0,4)
    current_positions = random.randint(0,4)
    future_positions = random.randint(0,4)
    jbt_id = 0
    for company in companies:
        for _ in range(past_positions):
            cur.execute(j_insert_query, (company, random.choice(positions), random.choice(status), random.choice(one_month_past_dates)))
            conn.commit()
            jbt_id += 1
            for _ in range(random.randint(1,6)):
                cur.execute(notes_insert_query, (jbt_id, lorem_ipsum))
                conn.commit()
        for _ in range(current_positions):
            cur.execute(j_insert_query, (company, random.choice(positions), random.choice(status), random.choice(current_month_dates)))
            conn.commit()
            jbt_id += 1
            for _ in range(random.randint(1,6)):
                cur.execute(notes_insert_query, (jbt_id, lorem_ipsum))
                conn.commit()
        for _ in range(future_positions):
            cur.execute(j_insert_query, (company, random.choice(positions), random.choice(status), random.choice(one_month_future_dates)))
            conn.commit()
            jbt_id += 1
            for _ in range(random.randint(1,6)):
                cur.execute(notes_insert_query, (jbt_id, lorem_ipsum))
                conn.commit()
    conn.commit()
    conn.close()

def fetch_notes(job_application_id):
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    notes = cur.execute(notes_fetch_query, (job_application_id,)).fetchall()
    conn.close()
    print(type(notes))
    print(notes)
    print(len(notes))
    for _note in notes:
        print(_note, end="\n==\n")
    return notes

def fetch_job_application(job_application_id: int)->JobApplication:
    conn = sqlite3.connect('jbt.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    job_application = JobApplication(**cur.execute(job_application_fetch_query, (job_application_id,)).fetchone())
    conn.close()
    print(job_application)
    return job_application

def update_job_application(job_application_id:int, new_status: str, next_date: str, next_time: str):
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    cur.execute(job_update_query, (new_status, f"{next_date} {next_time}", job_application_id,))
    conn.commit()
    conn.close()

def add_note(job_application_id:int, new_note:str):
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    cur.execute(notes_insert_query, (job_application_id, new_note,))
    conn.commit()
    conn.close()

def filter_job_applications(companies: List[str]=None, positions: List[str]=None, status:List[str]=None, _from:str="", _through: str="" )->List[JobApplication]:
    conn = sqlite3.connect('jbt.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    _params = ()

    result_query = "Select * from job_applications where "
    if companies is not None and len(companies) > 0:
        result_query += f"company in ({','.join(['?']*len(companies))}) "
        _params = _params + tuple(companies)
    if positions is not None and len(positions) > 0:
        result_query += f"and position in ({','.join(['?']*len(positions))}) "
        _params = _params + tuple(positions)
    if status is not None and len(status) > 0:
        result_query += f"and status in ({','.join(['?']*len(status))}) "
        _params = _params + tuple(status)
    if _from:
        result_query += "and next_deadline >= datetime(?) "
        _params = _params + (_from,)
    if _through:
        result_query += "and next_deadline <= datetime(?)" 
        _params = _params + (_through,)

    results = cur.execute(result_query, _params).fetchall()

    filtered_job_applications: List[JobApplication] = []
    
    for res in results:
        filtered_job_applications.append(JobApplication(**res))

    for j in filtered_job_applications:
        print(j)

    conn.close()


if __name__ == '__main__':
    init_db()
    # generate_data()
    
    # fetch_notes(152)
    
    # fetch_job_application(152)
    
    # update_job_application(job_application_id=152, new_status="Applied", next_date="2024-04-07", next_time="10:00")
    # fetch_job_application(152)

    # add_note(152, lorem_ipsum)
    # fetch_notes(152)

    # filter_job_applications(companies=["autodesk", "reef technologies", "hasura", "citadel", "2 sigma"],
    #     positions=["technical writer", "devops", "infra"],
    #     status = ["ready to apply", "ghosted", "interview scheduled", "rejected", "archived"],
    #     _from = "2024-02-28",
    #     _through = "2024-04-15",
    # )





from collections import namedtuple
from typing import List
import sqlite3

job_insert_query = "Insert into job_applications (company, position, status, next_deadline) values (?, ?, ?, ?)"
notes_insert_query = "Insert into notes (job_application_id, note) values (?, ?)"
job_application_fetch_query = "select * from job_applications where id = ?"
notes_fetch_query = "Select note from notes where job_application_id = ? ORDER BY id DESC"
job_update_query = "Update job_applications set status=?, next_deadline=? where id=?"
fetch_positions_query = "Select distinct position from job_applications"
fetch_companies_query = "Select distinct company from job_applications"


JobApplication = namedtuple("JobApplication", "id company position status next_deadline")

def init_db():
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        cur.executescript(f.read())
    conn.commit()
    conn.close()

def fetch_notes(job_application_id: int)->List[str]:
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    notes = cur.execute(notes_fetch_query, (job_application_id,)).fetchall()
    conn.close()
    return [_note[0] for _note in notes]

def fetch_job_application(job_application_id: int)->JobApplication:
    conn = sqlite3.connect('jbt.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    job_application = JobApplication(**cur.execute(job_application_fetch_query, (job_application_id,)).fetchone())
    conn.close()
    return job_application

def update_job_application(job_application_id:int, new_status: str, next_date: str, next_time: str):
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    cur.execute(job_update_query, (new_status, f"{next_date} {next_time}", job_application_id,))
    conn.commit()
    conn.close()

def add_job(company:str, pos: str, status: str, next_date: str, next_time:str):
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    cur.execute(job_insert_query, (company, pos, status, f"{next_date} {next_time}"))
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
    base_query = "Select * from job_applications"
    company_filter = ""
    position_filter = ""
    status_filter = ""
    from_filter = ""
    through_filter = ""
    result_query = ""
    if companies is not None and len(companies) > 0:
        company_filter= f"company in ({','.join(['?']*len(companies))}) "
        _params = _params + tuple(companies)
    if positions is not None and len(positions) > 0:
        position_filter = f"position in ({','.join(['?']*len(positions))}) "
        _params = _params + tuple(positions)
    if status is not None and len(status) > 0:
        status_filter = f"status in ({','.join(['?']*len(status))}) "
        _params = _params + tuple(status)
    if _from:
        from_filter = "next_deadline >= datetime(?) "
        _params = _params + (_from,)
    if _through:
        through_filter = "next_deadline <= datetime(?)" 
        _params = _params + (_through,)

    result_query = " and ".join([_filter for _filter in [company_filter, position_filter, status_filter, from_filter, through_filter] if _filter])

    result_query = base_query + " where " + result_query if len(_params) > 0 else base_query + result_query

    # print("====================")
    # print(result_query)
    # print("====================")

    results = cur.execute(result_query, _params).fetchall()
    filtered_job_applications: List[JobApplication] = []
    for res in results:
        filtered_job_applications.append(JobApplication(**res))
    conn.close()

    return filtered_job_applications


def fetch_positions() -> List[str]:
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    positions:List[str] =  [p[0] for p in cur.execute(fetch_positions_query).fetchall()]
    conn.close()
    return positions

def fetch_companies() -> List[str]:
    conn = sqlite3.connect('jbt.db')
    cur = conn.cursor()
    companies:List[str] =  [p[0] for p in cur.execute(fetch_companies_query).fetchall()]
    conn.close()
    return companies
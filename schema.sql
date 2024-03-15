CREATE TABLE IF NOT EXISTS job_applications(
   id INTEGER NOT NULL PRIMARY KEY,
   company TEXT NOT NULL,
   position TEXT NOT NULL,
   status TEXT NOT NULL,
   next_deadline TEXT
);

CREATE TABLE IF NOT EXISTS notes(
   id INTEGER NOT NULL PRIMARY KEY,
   job_application_id INTEGER NOT NULL,
   note TEXT NOT NULL,
   FOREIGN KEY (job_application_id)
       REFERENCES job_applications (id) 
);
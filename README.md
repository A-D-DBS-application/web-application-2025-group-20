[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)
solv.io MVP

solv.io is a data-driven web application designed to help professionals assess the financial solvability of debtors in a structured and transparent way. The platform enables authorized users to create and manage debtor profiles and to consult financial data originating from external sources. Each debtor can be linked to zero, one, or multiple yearly financial records, allowing financial trends and evolutions to be analysed over time.

To support compliance and accountability, all interactions with sensitive debtor data are automatically recorded in an audit log, ensuring full traceability of data access and modifications. Additionally, solv.io includes a value-adding solvability scoring mechanism based on key financial indicators supporting better-informed risk assessments.

By combining centralized data management, auditability, and lightweight financial analytics, solv.io helps organizations reduce credit risk while maintaining control over sensitive financial information.



## Installation and Running the Application

To run this Flask application locally, Python 3.10 or higher must be installed. First, clone the repository and navigate to the project directory. Next, create a virtual environment and activate it. On Windows, use `python -m venv .venv` followed by `.venv\Scripts\activate`. On macOS or Linux, use `python3 -m venv .venv` and `source .venv/bin/activate`.

Once the virtual environment is activated, install the required dependencies using `pip install -r requirements.txt`. If the requirements file is not present, install the dependencies manually using `pip install flask flask_sqlalchemy psycopg2-binary python-dotenv`.

The application uses a PostgreSQL database hosted on Supabase. Create a `.env` file in the root directory and add the database connection string using the variable `DATABASE_URL`. This connection string can be obtained from the Supabase project settings.

After completing these steps, the application can be started by running `python run.py` (or explicitly `.venv\Scripts\python.exe run.py` on Windows). The Flask application will be available at `http://127.0.0.1:5000`.

## Notes

Authentication is intentionally simplified (username only, no password). The focus of this project is on core MVP functionality and not on production-level security. The database structure is documented using an ERD and corresponding DDL scripts included in the repository.

Webapplication:
https://web-application-2025-group-20.onrender.com/

User stories:
https://docs.google.com/document/d/1C9TwLObmLnId3NByVFbiuS_lEH_pztyXOLUHI1_d5h8/edit?usp=sharing

Demo video:
https://www.loom.com/share/d396203f65634104b2a6b57cdff34e82

Powerpoint:
https://docs.google.com/presentation/d/1WCyxSuXJUPxY-l5cg-bXd5Erf6RocgO9/edit?slide=id.p11#slide=id.p11
https://docs.google.com/presentation/d/1WCyxSuXJUPxY-l5cg-bXd5Erf6RocgO9/edit?usp=drive_link&ouid=109654379017766781848&rtpof=true&sd=true




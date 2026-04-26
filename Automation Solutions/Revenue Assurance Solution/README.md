# Revenue Assurance (RA) Automated ETL Pipeline

## 📌 The Problem
The Revenue Assurance department requires daily Network KPI reports for financial reconciliation. Previously, this process was manual:
* Downloading multiple CSV files from a source SFTP.
* Manually filtering specific columns and rows.
* Consolidating data into a single report.
* Uploading the final result to a different RA-managed SFTP.
This manual process took ~30 minutes daily and was prone to human error during data filtering.

## 🛠 My Solution
I developed a standalone Python-based ETL (Extract, Transform, Load) automation tool. Compiled into a lightweight executable and managed via a Windows/Task Scheduler, it runs every morning without human intervention.

### Key Technical Features:
* **Multi-Server Orchestration:** Securely interfaces with two distinct SFTP servers using **Paramiko** to move data across network boundaries.
* **Automated Data Transformation:** Parses daily CSV exports, extracts specific target KPI columns, and consolidates fragmented data into a single, clean master file.
* **Temporal Logic:** Automatically calculates folder paths based on the previous day's timestamp to ensure data continuity.
* **Cleanup Logic:** Implements automatic local file deletion post-upload to maintain server storage health and data privacy.

## 💻 Logic Showcase
* **Selective Extraction:** Instead of copying whole files, the script identifies specific indices of `TARGET_COLUMNS` to ensure the final report contains only the data requested by the RA department.
* **Secure Configuration:** Utilizes `.env` files to keep SFTP credentials out of the source code, maintaining security best practices.

## 📈 Business Impact
* **Efficiency:** Fully automated a daily task, saving **30 minutes per day** (approx. 180 hours/year).
* **Reliability:** Guaranteed that reports are ready for the RA team every morning at the same time, with zero manual entry errors.
* **Zero Footprint:** Delivered as a standalone `.exe`, requiring no Python installation on the production server.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*
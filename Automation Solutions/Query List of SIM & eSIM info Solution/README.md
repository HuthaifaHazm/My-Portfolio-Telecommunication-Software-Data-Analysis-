# Enterprise ICCID Query & Validation System (Active Directory Integrated)

## 📌 The Problem
Managing and auditing massive batches of SIM/eSIM ICCIDs was previously a manual, spreadsheet-heavy process. It lacked:
1. **Security:** No formal authentication for data access.
2. **Scalability:** Handling thousands of ICCIDs at once would crash simple scripts.
3. **Data Integrity:** Manual entry often resulted in invalid ICCID lengths or incorrect prefixes.
This tool was developed to provide a secure, high-speed portal for bulk ICCID auditing, saving ~30-60 minutes of daily manual effort.

## 🛠 My Solution
I developed a **Distributed Full-Stack Application** featuring a Flask Frontend, a Secure API Backend, and a PostgreSQL Database. It allows users to query thousands of ICCIDs simultaneously via Excel upload or numerical range.

### Key Technical Features:
* **LDAP/Active Directory Authentication:** Fully integrated with corporate security via the `ldap3` library, supporting email-based login and authorized user whitelisting.
* **Tiered Security Architecture:** * **Frontend:** Manages sessions and file parsing.
    * **Backend:** Handles business logic and LDAP communication.
    * **Database:** High-performance PostgreSQL storage for SIM/eSIM records.
* **Intelligent Batch Processing:** * Parses multi-sheet Excel files using `Pandas` and `Openpyxl`.
    * Includes a regex-based validation engine to verify ICCID lengths and carrier prefixes.
* **Security Hardening:** Implemented a custom anti-brute force mechanism to track and block failed login attempts.
* **Automated Export:** Generates formatted, audit-ready Excel reports directly from database query results.

## 💻 Logic Workflow
1. **Verify:** User logs in via Active Directory.
2. **Ingest:** User uploads an Excel file or enters an ICCID range.
3. **Validate:** The FE identifies the SIM group (SIM vs eSIM) and validates the numeric format.
4. **Retrieve:** The BE executes a batch query (`ANY(%s)`) against the relevant database table for maximum performance.
5. **Export:** Results are compiled into a downloadable .xlsx file for the Commercial team.

## 📈 Business Impact
* **Efficiency:** Automated the identification of SIM batches, reducing lookup time from hours to seconds.
* **Governance:** Centralized data access through Active Directory, ensuring only authorized personnel can view sensitive SIM data.
* **User Experience:** Provided a professional web interface that handles all complex data formatting in the background.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*
# Multi-Tier eSIM Management & Diagnostics System

## 📌 Project Overview
This project is a distributed enterprise solution designed for Telecommunications Call Centers. It enables back-office agents to manage eSIM lifecycles, generate activation QR codes, and perform real-time diagnostics on device-network compatibility.

The system is split into two specialized servers to ensure security and load distribution.

### System Architecture
1.  **Customer-Facing API (Server 1):**
    * Manages User Authentication and Session state.
    * Interfaces with eSIM Cloud Providers via secure SSL/TLS certificates.
    * Generates on-the-fly QR codes for eSIM activation.
2.  **Network Operations Backend (Server 2):**
    * Interfaces with PostgreSQL databases for subscriber records.
    * **Core NE Integration:** Uses SSH (Paramiko) to query live Network Elements for active IMEI data.
    * **Device Intelligence:** Maps Type Allocation Codes (TAC) to device models using Pandas-based lookups.

## 🛠 Tech Stack
* **Framework:** Flask (Python)
* **Database:** PostgreSQL (psycopg2)
* **Automation:** Paramiko (SSH), Requests (REST)
* **Data Science:** Pandas (for TAC mapping)
* **Utilities:** Luhn Algorithm implementation, QR Code Generation, Dotenv

---

## 🚀 Key Features & Logic

### 1. Real-Time Device Diagnostics
The system fetches a live IMEI from the core network and cross-references the first 8 digits (TAC) against a master database to identify the specific device model being used by the customer.

### 2. Distributed Authentication
Communication between the Frontend and Backend servers is secured via an **API Key (X-API-KEY)** header, ensuring the internal database server only responds to authorized requests.

### 3. Data Integrity & Validation
Includes a custom implementation of the **Luhn Algorithm** to calculate check digits for ICCIDs, ensuring that generated QR codes and network queries are mathematically valid before transmission.

---

📈 Impact
By implementing this automation, the ticket resolution time was saved 1.5 hours. 
Significantly improving the Quality of Service (QoS) and operational efficiency within the core department.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*
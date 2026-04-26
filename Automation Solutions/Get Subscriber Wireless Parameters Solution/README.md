# RF Subscriber Diagnostics & Cell-Site Mapping Tool

## 📌 The Problem
RF (Radio Frequency) engineers often need to track which specific cell site and sector a subscriber is currently latched to for troubleshooting network interference or handovers. Traditionally, this required:
* Manually logging into Core Network Elements.
* Running complex CLI commands and manually parsing raw hex output.
* Decoding hex values (like TMSI or eNBID) into readable decimal formats.

## 🛠 My Solution
I developed a rapid-diagnostic web interface that automates the entire SSH-to-CLI workflow. The tool allows RF engineers to simply enter an MSISDN or IMSI and receive immediate, human-readable network location data.

### Key Technical Features:
* **Automated Network Scraping:** Uses **Paramiko** to establish secure SSH sessions and execute real-time queries on the Core.
* **Hex-to-Decimal Decoding:** Automatically converts technical identifiers (TMSI, eNBID) from hexadecimal to decimal for immediate use in RF planning tools.
* **Modern Deployment Stack:** * **Frontend/Backend:** Built with PyWebIO and Flask.
    * **Security:** Deployed behind an **Nginx Reverse Proxy** with HTTPS/TLS encryption.
    * **Access Control:** Secured via Nginx-level authentication to ensure only authorized RF personnel can access network data.

## 💻 Logic Showcase
* **Regex Parsing:** Implements complex regular expressions to extract multiple network parameters (MSISDN, TMSI, Sector) from non-structured CLI responses.
* **Input Intelligence:** The script automatically detects if the user entered an IMSI or MSISDN and adjusts the network command syntax accordingly.

## 📈 Business Impact
* **Time Savings:** Reduced the daily troubleshooting workload for the RF department by **2 hours per day**.
* **Error Reduction:** Eliminated manual hex-to-decimal conversion errors, ensuring engineers are looking at the correct cell sites.
* **Accessibility:** Moved a "CLI-only" task to a secure web interface, allowing for faster diagnostics in the field.

---

## 👨‍💻 Author
**Huthaifa Hazem Ismail**
*Telecommunications Engineer & Data Analyst & Software Development*
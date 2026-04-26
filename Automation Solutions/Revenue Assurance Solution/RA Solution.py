import paramiko
import datetime
import os
import csv
from dotenv import load_dotenv

load_dotenv()

SFTP1_HOST = os.getenv("SFTP1_HOST")
SFTP1_PORT = os.getenv("SFTP1_PORT")
SFTP1_USERNAME = os.getenv("SFTP1_USERNAME")
SFTP1_PASSWORD = os.getenv("SFTP1_PASSWORD")
SFTP2_HOST = os.getenv("SFTP2_HOST")
SFTP2_PORT = os.getenv("SFTP2_PORT")
SFTP2_USERNAME = os.getenv("SFTP2_USERNAME")
SFTP2_PASSWORD = os.getenv("SFTP2_PASSWORD")
SFTP1_Path = os.getenv("SFTP1_Path")
SFTP2_Path = os.getenv("SFTP2_Path")
Local_Path = os.getenv("Local_Path")
Local_Path2 = os.getenv("Local_Path2")

TARGET_COLUMNS = [
    "C1",
    "C2",
    "C3",
    "C4",
]

os.makedirs(Local_Path, exist_ok=True)

def main():
    transport = paramiko.Transport((SFTP1_HOST, SFTP1_PORT))
    transport.connect(username=SFTP1_USERNAME, password=SFTP1_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    today2 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    today = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")

    today_folder_name = f"pmexport_{today}"
    today_folder_path = f"{SFTP1_Path}/{today_folder_name}"

    try:
        files = sftp.listdir(today_folder_path)
    except FileNotFoundError:
        return

    FILE_PREFIX = "XXXXX_"

    for file in files:
        if file.endswith(".csv") and file.startswith(FILE_PREFIX):
            remote_file = f"{today_folder_path}/{file}"
            local_file = os.path.join(Local_Path, file)
            sftp.get(remote_file, local_file)

    sftp.close()
    transport.close()



    final_rows = []
    header_written = False

    for file in sorted(os.listdir(Local_Path)):
        if not file.endswith(".csv"):
            continue
        
        file_path = os.path.join(Local_Path, file)
        with open(file_path, newline="") as csvfile:
            reader = list(csv.reader(csvfile))
            header = reader[0]
            side1 = reader[2]
            side2 = reader[3]
            col_idx = [header.index(col) for col in TARGET_COLUMNS]
            filtered_side1 = [side1[i] for i in col_idx]
            filtered_side2 = [side2[i] for i in col_idx]
            if not header_written:
                final_rows.append(TARGET_COLUMNS)
                header_written = True

            final_rows.append(filtered_side1)
            final_rows.append(filtered_side2)

    OUTPUT_FILE = os.path.expanduser(f"{SFTP2_Path}/ZZZZ.csv")
    with open(OUTPUT_FILE, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(final_rows)

    for file in sorted(os.listdir(Local_Path)):
        os.remove(os.path.join(Local_Path, file))

    local_folder = os.path.expanduser(Local_Path2)
    filename = "ZZZZ.csv"

    try:
        transport = paramiko.Transport((SFTP2_HOST, SFTP2_PORT))
        transport.connect(username=SFTP2_USERNAME, password=SFTP2_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        local_file = os.path.join(local_folder, filename)
        remote_path = f'{SFTP2_Path}{filename}'
        sftp.put(local_file, remote_path)
        os.remove(local_file)

        sftp.close()
        transport.close()
    except Exception as e:
        pass

if __name__ == "__main__":
    main()

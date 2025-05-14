from Application.Website.CMA import CMA
from datetime import datetime
import pandas as pd

INPUT_FILE_PATH = r"D:\clonedrepos\Maersk-Shipments-Scraper-Automation-main\INPUT.csv"
if INPUT_FILE_PATH.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx"):
    df = pd.read_excel(INPUT_FILE_PATH)
    
# Convert the first column to a list of BL numbers
first_col_list = df.iloc[:, 0].dropna().unique().tolist()
cma = CMA("https://www.cma-cgm.com/ebusiness/tracking/search")
cma.start(first_col_list)
milestone_keys = ['Gate in', 'Departure', 'Arrival', 'Discharge', 'Pull Out']
datalist = []
for shipment in cma.shipments:
    shipment_id = shipment.shipment_id
    for container in shipment.containers:
        container_id = container.container_id
        shipment_data = {"Shipment ID": shipment_id,
                          "Container ID": container_id,
                          "Gate in": None,
                          "Arrival": None,
                          "Departure": None,
                          "Discharge": None,
                          "Pull Out": None}
        for milestone in container.milestones:
            if milestone.event not in milestone_keys:
                    continue  # skip unnecessary milestones

                # this control flow records the first occurrence of Gate in and Departure
                # and the last occurrence of Arrival, Discharge, and Gate out for delivery

            if (shipment_data[milestone.event] is not None and milestone.event not in ["Gate in", "Departure"]) or (shipment_data[milestone.event] is None):
                shipment_data[milestone.event] = milestone.date
                if milestone.event in ["Arrival", "Departure"]:
                    shipment_data[f"{milestone.event} Vessel Name"] = milestone.vessel_name
                    shipment_data[f"{milestone.event} Voyage ID"] = milestone.vessel_id 
        shipment_data["Status"] = "Completed" if container.status else "On-going"
        shipment_data['Scraped at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        datalist.append(shipment_data)

if cma.failed_shipments:
    print(f"Failed to extract data in {len(cma.failed_shipments)} shipments")
    print("Check the Failed_Shipment_Extractions.csv file for more details")
    print('Rerun the script to extract data in the failed shipments.')
    print('Do not forget to update the INPUT_FILE_PATH variable to the path of the failed shipments file.')
    print('Do not forget to update the OUTPUT_FILE_PATH variable to new path.')
else:
    print(f"Successfully extracted data in {len(cma.shipments)} shipments")
    print("Check the OUTPUT.csv file for the extracted data")
    print(f"Processed {len(cma.shipments)}/{len(first_col_list)} shipments")
    
df = pd.DataFrame(cma.failed_shipments, columns=['Shipment ID'])
df.to_csv("Failed_Shipment_Extractions.csv", index=False)

output_df = pd.DataFrame(datalist)
output_df.to_csv("OUTPUT.csv", index=False)
cma.close()




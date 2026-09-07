import os
import pandas as pd


def ingest_excel(file_path, output_folder="docs"):
    """
    Extract important sheets from an Excel workbook
    and save each sheet as a separate text file.
    """

    # Create docs folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load workbook
    xls = pd.ExcelFile(file_path)

    # Important sheet names / keywords
    important_keywords = [
        "histor",
        "forecast",
        "wacc",
        "dcf",
        "comp",
        "valuation",
        "income",
        "balance",
        "cash"
    ]

    documents = []
    extracted_sheets = []

    # Loop through all sheets
    for sheet in xls.sheet_names:

        # Keep only important sheets
        if any(keyword in sheet.lower() for keyword in important_keywords):

            df = pd.read_excel(
                file_path,
                sheet_name=sheet,
                header=None
            )

            # Replace NaN with empty string
            df = df.fillna("")

            rows = []

            # Convert every row into text
            for _, row in df.iterrows():

                row_text = " | ".join(
                    str(cell)
                    for cell in row
                    if str(cell).strip() != ""
                )

                if row_text:
                    rows.append(row_text)

            sheet_text = "\n".join(rows)

            documents.append(
                {
                    "sheet": sheet,
                    "content": sheet_text
                }
            )

            extracted_sheets.append(sheet)

    # Save every sheet as text file
    for doc in documents:

        filename = os.path.join(
            output_folder,
            f"{doc['sheet']}.txt".replace("/", "_")
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(doc["content"])

    print(f"Successfully extracted {len(documents)} sheets.")

    return extracted_sheets


# ------------------------------
# Run directly
# ------------------------------

if __name__ == "__main__":

    FILE_PATH = "data/Godrej Consumer.xlsx"

    ingest_excel(FILE_PATH)
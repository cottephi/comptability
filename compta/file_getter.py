# file_getter.py
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
from typing import Union, Dict, List
from .logger import log as logger

all_months = [
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


def get_drive_api(cred: Path):
    logger.info("Connecting too Google Drive...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file(str(cred), scopes=scopes)
    # spreadsheet_service = build("sheets", "v4", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    logger.info("... connected")
    return drive_service


def download_compta_files(filenames: List[str], output_dir: Path, cred: Path, prgbar=None, ntotalfiles=None) -> bool:
    # sheet = spreadsheet_service.spreadsheets().get(
    #     spreadsheetId="1AsuG88PcH1FPhsY457HW6LKpV4zG1bncE1OhFSD9qLA"
    # ).execute()
    # print(sheet)

    query_body = "mimeType='application/vnd.google-apps.spreadsheet'"
    drive_service = get_drive_api(cred)

    logger.info(f"Downloading spreadsheets...")
    if prgbar is not None:
        if ntotalfiles is None:
            prgbar["download"].update(0)
        else:
            prgbar["download"].update(ntotalfiles - len(filenames))
    files_service = drive_service.files()
    files = files_service.list(q=query_body).execute().get("files")
    found_files = []
    for afile in files:
        if afile["name"] in filenames:
            found_files.append(afile)
            break

    if len(found_files) == 0:
        logger.warning(f"No Google Sheets found for {filenames}.")
        return False

    excel_mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    for i, compta in enumerate(found_files):
        if prgbar is not None:
            prgbar.read(timeout=0)
        name = compta["name"]
        logger.info(f"  Downloading {name}...")
        compta = files_service.export(fileId=compta["id"], mimeType=excel_mime_type).execute()

        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)

        outfilepath = output_dir / f"{name}.xlsx"
        with open(str(outfilepath), "wb") as f:
            f.write(compta)
        if not outfilepath.is_file():
            logger.warning(f"Could not download excel file {name}")
            continue
        if prgbar is not None:
            prgbar["download"].update(i + 1)

        logger.info(f"  ...downloaded {outfilepath}")
    logger.info(f"...downloaded spreadsheets")


def get_excels(
    filenames: List[str], fetch: bool, output_dir: Path, cred: Path, months: Union[None, str, List[str]], prgbar=None
) -> Dict[str, Dict[str, pd.DataFrame]]:

    filepaths = [(Path(output_dir) / filename).with_suffix(".xlsx") for filename in filenames]

    if fetch:
        download_compta_files(filenames=filenames, output_dir=output_dir, cred=cred, prgbar=prgbar)
    else:
        missing_files = []
        for filepath in filepaths:
            if not filepath.is_file():
                missing_files.append(filepath.stem)

        if len(missing_files) > 0:
            download_compta_files(
                filenames=missing_files, output_dir=output_dir, cred=cred, prgbar=prgbar, ntotalfiles=len(filenames)
            )
        elif prgbar is not None:
            prgbar["download"].update(len(filenames))

    dfs = {}

    logger.info("")
    logger.info("Opening years files...")
    if prgbar is not None:
        prgbar["get_months"].update(0)
        prgbar["open_years"].update(0)

    for i, filepath in enumerate(filepaths):
        year = filepath.stem.split("_")[-1]
        if not filepath.is_file():
            logger.warning(f"No file available for year {year}")
            continue

        if prgbar is not None:
            prgbar.read(timeout=0)

        logger.info(f"  Opening '{filepath}'...")
        if months is not None:
            if not isinstance(months, list):
                months = [months]
        else:
            months = all_months
        dfs[year] = {}

        for j, month in enumerate(months):
            try:
                logger.info(f"    Getting month '{month}'...")
                dfs[year][month] = pd.read_excel(str(filepath), sheet_name=month, header=None)
                dfs[year][month].index.name = month
                logger.info(f"    ...got month '{month}'")
                if prgbar is not None:
                    prgbar[f"get_months"].update(j + 1)
            except ValueError as e:
                if "Worksheet named" in str(e) and "not found" in str(e):
                    logger.info(f"    Month '{month}' is not available. Skipping.")
                    dfs[year][month] = pd.DataFrame()
                    if prgbar is not None:
                        prgbar[f"get_months"].update(j + 1)
                    continue
                raise e

        if prgbar is not None:
            prgbar[f"open_years"].update(i + 1)
        logger.info(f"  ...opened '{filepath}'")
    logger.info(f"...opened years files")
    return dfs

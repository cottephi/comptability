# main.py
import argparse
from pathlib import Path
from compta.file_reader import read_excel
from compta.plotter import graph_plotter
from compta.logger import log as logger

if __name__ == "__main__":
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description="Compta", formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
    parser.add_argument(
        "-f",
        "--fetch",
        action="store_true",
        help="If the Google Sheet is already present locally,"
        " the program does not download it, unless --fetch is specified.",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default="compta",
        help="Google Sheet name on Google Drive (no extensions). Default is 'compta'",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="outputs", help="Output directory. Default is 'outputs'",
    )
    parser.add_argument(
        "-c",
        "--credentials",
        type=str,
        default="credentials.json",
        help="json file with service account credentials. Default is 'credentials.json'",
    )
    parser.add_argument(
        "-m",
        "--months",
        type=str,
        default=None,
        help="Months to analyse. If not specified, analyses all available months. Format must be 'Janvier,Fevrier,...'",
    )
    parser.add_argument(
        "-y",
        "--years",
        type=str,
        default="2021",
        help="Years to analyse. Default to 2021. Format must be 'Janvier,Fevrier,...'",
    )
    args = parser.parse_args()

    fetch = args.fetch
    filename = args.name
    cred = Path(args.credentials)
    output = Path(args.output)
    months = args.months
    years = args.years
    if months is not None:
        months = months.replace(" ", "").split(",")
    years = years.replace(" ", "").split(",")
    graph_plotter(
        dataframe=read_excel(
            filename=filename, fetch=fetch, output_dir=output, cred=cred, months=months, years=years, prgbar=None
        ),
        output=str(Path(output) / f"{filename}.html"),
    )
    logger.info("\nProgram ended sucessfully")

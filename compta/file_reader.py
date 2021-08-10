# file_formatter
from .logger import log as logger
from .file_getter import get_excels
import pandas as pd
from pathlib import Path
from typing import Optional, Union, List


processed = []  # list of (line, column_start) of each categories. Used to avoid redundancy


def clean():
    global processed
    processed = []


def find_category(
    excel: pd.DataFrame,
    parents: dict,
    dataframe: pd.DataFrame,
    depth: int = 0,
    line: Optional[int] = None,
    column_start: Optional[int] = None,
    column_end: Optional[int] = None,
    max_depth: Optional[int] = None,
) -> pd.DataFrame:
    global processed

    for ic in excel.iloc[line].index[column_start:column_end]:
        thedepth = depth
        item = excel.iloc[line, ic]
        if isinstance(item, str):
            # Item is a string -> a category name
            category = item
            category_id = f"{item}_{line}_{ic}"

            # noinspection PyProtectedMember
            if category_id in processed:
                # The category has already been processed : skip
                continue

            item_below = excel.iloc[line + 1, ic]
            if isinstance(item_below, str):
                # Item in the cell below is a string too : the category we found contains others. Fetch them.

                # Get the last column of the category : it is the next cell having a non-nan float.
                last_column = None
                for lc in excel.iloc[line].index[ic + 1: column_end]:
                    maybe_total = excel.iloc[line, lc]
                    if isinstance(maybe_total, str):
                        raise ValueError(
                            f"Malformed Sheet : Could not find total for category {category},"
                            f" got another category name instead: {item_below}"
                        )
                    if not pd.isna(maybe_total):
                        last_column = lc + 1
                        thedepth += 1
                        parents[f"category_{thedepth}"] = category
                        dataframe = find_category(
                            excel=excel,
                            parents=parents,
                            dataframe=dataframe,
                            depth=thedepth,
                            line=line + 1,
                            column_start=ic,
                            column_end=last_column,
                        )
                        break
                if last_column is None:
                    raise ValueError(
                        f"Malformed Sheet : Could not find total for category {category}, reached end of file"
                    )

            else:
                # Item in the cell below is not string : the category we found is a final one. Fetch its total and save
                # it
                i = 2
                while pd.isna(item_below):
                    if i >= len(excel.index) and isinstance(item_below, str):
                        raise ValueError(
                            f"Malformed Sheet : Could not find total for category {category}, reached end of file"
                        )
                    item_below = excel.iloc[line + i, ic]
                    i += 1
                    if isinstance(item_below, str):
                        raise ValueError(
                            f"Malformed Sheet : Could not find total for category {category},"
                            f" got another category name instead: {item_below}"
                        )
                # Item in the cell below is a number : it is the category's total
                # TODO : recompute total from cells below?
                thedepth += 1
                parents[f"category_{thedepth}"] = category
                if max_depth is not None:
                    for i in range(max_depth):
                        thedepthforfuckingstupidplotly = i + 1
                        parents[f"category_{thedepthforfuckingstupidplotly}"] = None

                all_columns = list(set(list(dataframe.columns) + list(parents.keys())))
                dataframe = dataframe.reindex(all_columns, axis=1)
                newline = pd.Series(index=list(parents.keys()) + ["total"], data=list(parents.values()) + [item_below])
                newline.name = len(dataframe)
                dataframe = dataframe.append(newline)

            processed.append(category_id)
    return dataframe


def read_excel(
    filename: str,
    fetch: bool,
    output_dir: Path,
    cred: Path,
    months: Union[None, str, List[str]],
    years: List[str],
    prgbar=None,
) -> pd.DataFrame:

    categories = []
    filenames = [f"{filename}_{year}" for year in years]
    excels = get_excels(filenames, fetch, output_dir, cred, months, prgbar)

    logger.info("")
    logger.info(f"Reading years...")

    if prgbar is not None:
        prgbar["read_years"].update(0)
        prgbar["read_months"].update(0)

    logger.warning(f"Fetching max depth...")
    for i, year in enumerate(excels):
        if len(excels[year]) == 0:
            logger.warning(f"Could not get year {year}")
            continue
        for j, month in enumerate(excels[year]):
            categories.append(read_one_excel(excels[year][month], month, year))
    categories = pd.concat(categories, ignore_index=True)
    max_depth = len(categories.columns) - 2  # remove 1 for Years and 1 for Months

    categories = []
    for i, year in enumerate(excels):
        if len(excels[year]) == 0:
            logger.warning(f"Could not get year {year}")
            continue
        logger.info(f"  Reading months for year {year}...")
        for j, month in enumerate(excels[year]):
            categories.append(read_one_excel(excels[year][month], month, year, max_depth=max_depth))
            if prgbar is not None:
                prgbar[f"read_months"].update(j + 1)

        if prgbar is not None:
            prgbar[f"read_years"].update(i + 1)
        logger.info(f"  ...months read for {year}")

    logger.info(f"...years read")
    categories = pd.concat(categories, ignore_index=True)
    filepath = (Path(output_dir) / filename).with_suffix(".csv")
    # noinspection PyTypeChecker
    categories.to_csv(str(filepath))
    return categories


def read_one_excel(excel: pd.DataFrame, month, year: str, max_depth: Optional[int] = None) -> pd.DataFrame:
    logger.info(f"    Reading month {month}...")
    categories = pd.DataFrame(columns=["Year", "Month", "total"])
    for line in excel.index:
        categories = find_category(
            excel=excel, parents={"Year": year, "Month": month}, dataframe=categories, line=line, column_start=None, max_depth=max_depth
        )
    cat_columns = [c for c in categories.columns if "category" in c]
    cat_columns.sort()
    categories = categories.reindex(["Year", "Month"] + cat_columns + ["total"], axis=1)
    logger.info(f"    ...read month {month}")
    clean()
    return categories


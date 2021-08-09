from pathlib import Path
from compta.file_reader import read_excel
from compta.plotter import graph_plotter
from compta.logger import log as logger
import json


project_path = Path(__file__).parent.parent


def test_main():
    fetch = True
    filename = "compta"
    cred = project_path / "credentials.json"
    output = project_path / "tests" / "data" / "outputs"
    months = ["test_1", "test_2"]
    graph_plotter(read_excel(filename, fetch, output, cred, months))
    logger.info("\nProgram ended sucessfully")

    with open("tests/data/outputs/compta.json", "r") as f:
        result = json.load(f)
    with open("tests/data/expected.json", "r") as f:
        expected = json.load(f)
    for month_result, month_expected in zip(result.keys(), expected.keys()):
        print("\n", month_result, month_expected)
        assert month_result == month_expected
        for table_result, table_expected in zip(result[month_result], expected[month_expected]):
            print("\n  ", table_result, table_expected)
            assert table_result == table_expected
            assert (
                result[month_result][table_result]["total"]
                == expected[month_expected][table_expected]["total"]
            )
            for detail_result, detail_expected in zip(
                result[month_result][table_result]["detail"],
                expected[month_expected][table_expected]["detail"],
            ):
                print("\n    ", detail_result, detail_expected)
                print(result[month_result][table_result]["detail"][detail_result])
                print(expected[month_expected][table_expected]["detail"][detail_expected])
                assert detail_result == detail_expected
                assert (
                    result[month_result][table_result]["detail"][detail_result]
                    == expected[month_expected][table_expected]["detail"][detail_expected]
                )

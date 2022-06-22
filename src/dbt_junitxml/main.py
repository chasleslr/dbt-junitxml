import click
import json

from junit_xml import TestCase, TestSuite, to_xml_report_string


class InvalidRunResult(Exception):
    pass


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "run_result",
    type=click.Path(exists=True)
)
@click.argument(
    "output",
    type=click.Path(exists=False)
)
def parse(run_result, output):
    with open(run_result) as f:
        run_result = json.load(f)

    try:
        rpc_method = run_result["args"]["rpc_method"]
        schema_version = run_result["metadata"]["dbt_schema_version"]

        if not schema_version == "https://schemas.getdbt.com/dbt/run-results/v4.json":
            raise InvalidRunResult("run_result.json other than v4 are not supported.")

        if not rpc_method in ["test", "build"]:
            raise InvalidRunResult(f"run_result.json must be from the output of `dbt test` or `dbt build`. Got dbt {rpc_method}.")

    except KeyError as e:
        raise InvalidRunResult(e)

    def is_test(dict):
        return dict["unique_id"].split(".")[0] == 'test'

    tests = [d for d in run_result['results'] if is_test(d)]

    test_cases = []
    for test in tests:
        test_case = TestCase(
            classname=test["unique_id"],
            name=test["unique_id"].split(".")[-2],
            elapsed_sec=test["execution_time"],
            status=test["status"],
        )

        if test["status"] == "fail":
            test_case.add_failure_info(message=test["message"])

        if test["status"] == "error":
            test_case.add_error_info(message=test["message"])

        if test["status"] == "skipped":
            test_case.add_skipped_info(message=test["message"])

        test_cases.append(test_case)

    test_suite = TestSuite("Tests", test_cases=test_cases)

    xml_report = to_xml_report_string([test_suite])

    with open(output, mode="wb") as o:
        o.write(xml_report.encode())

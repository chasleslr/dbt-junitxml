import json

import click
from junit_xml import TestCase, TestSuite, to_xml_report_string


class InvalidRunResult(Exception):
    pass


@click.group()
def cli():
    pass


@cli.command()
@click.argument("run_result", type=click.Path(exists=True))
@click.argument("output", type=click.Path(exists=False))
def parse(run_result, output):
    with open(run_result) as f:
        run_result = json.load(f)

    try:
        executed_command = (
            run_result["args"]["which"]
            if "which" in run_result["args"].keys()
            else run_result["args"]["rpc_method"]
        )

        if not executed_command == "test":
            raise InvalidRunResult(
                f"run_result.json must be from the output of `dbt test`. Got dbt {executed_command}."
            )

    except KeyError as e:
        raise InvalidRunResult(e)

    tests = run_result["results"]

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

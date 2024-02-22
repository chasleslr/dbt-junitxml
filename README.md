# dbt-junitxml

Convert your dbt test results into jUnit XML format so that CI/CD platforms (such as Jenkins, CircleCI, etc.)
can better report on tests in their UI.

## About this fork

This is the fork repository based on https://github.com/chasleslr/dbt-junitxml/ version 0.1.5  
On top of that here were added:  
1. Support of DBT Core 1.3+ (originally it supported only up to 1.2). Versions 0.2.x Tested on DBT 1.5
2. In case of test failures Junit XML contains additional information regarding Stored Results and original test SQL. Details can be found below.
3. Test name in the resulted xml is more specific rather than in original version .
4. Supported integration with https://reportportal.io/

## Installation

Publishing as a regular pip module is considered

```shell
pip install "git+https://github.com/SOVALINUX/dbt-junitxml@0.2.1#egg=dbt-junitxml"
```

We recommend you to stick to some specific version, since newer versions might contain changes that may impact your operations (not being backward incompatible at all, but rather change some visualizations you might be used to).  

## Usage

When you run your dbt test suite, the output is saved under `target/run_results.json`. Run the following command
to parse your run results and output a jUnit XML formatted report named `report.xml`.

```shell
dbt-junitxml parse target/run_results.json report.xml
```

## Features description

### Rich XML output in case of test failure
  
In order to help you handle test failures right where you see it we're adding supporting information into Junit XML in case of test failure  
It's even more than you see in the DBT CLI console output!  
For example:  

```
Got 19 results, configured to fail if != 0
2023-06-08 10:47:02
------------------------------------------------------------------------------------------------
select * from db_dbt_test__audit.not_null_table_reporter_employee_id
------------------------------------------------------------------------------------------------

select *
from (select * from "datacatalog"."db"."table" where NOT regexp_like(reporter_email_address, 'auto_.*?@company.com') AND reporter_email_address NOT IN ('exclude@company.com') AND reporter_email_address IS NOT NULL) dbt_subquery
where reporter_employee_id is null
```

### Saving test SQL files for further analysis

Sometimes it's handy to see the exact SQL that was executed and tested by DBT without repeating compilation steps.  
To achieve it we suggest you to save compiled tests SQL during your test run.  
Below you can find a reference script:  
```shell
dbt test --store-failures
mkdir -p target/compiled_all_sql && find target/compiled/ -name *.sql -print0 | xargs -0 cp -t target/compiled_all_sql/
zip -r -q compiled_all_sql.zip target/compiled_all_sql
```

### Integration with Report Portal

https://reportportal.io/ helps you to manage your test launches. Here at EPAM we're using this tool to manage over 4,000 DBT tests  

In order to upload your test run to reportportal you can use the following script:
```shell
dbt-junitxml parse target/run_results.json target/manifest.json dbt_test_report.xml
zip dbt_test_report.zip dbt_test_report.xml
REPORT_PORTAL_TOKEN=`Your token for Report Portal`
RESPONSE=`curl -X POST "https://reportportal.io/api/v1/epm-plxd/launch/import" -H  "accept: */*" -H  "Content-Type: multipart/form-data" -H  "Authorization: bearer ${REPORT_PORTAL_TOKEN}" -F "file=@dbt_test_report.zip;type=application/x-zip-compressed"`
LAUNCH_ID=`echo "${RESPONSE}" | sed 's/.*Launch with id = \(.*\) is successfully imported.*/\1/'`
```

## Limitations

Currently, only v4 of the [Run Results](https://docs.getdbt.com/reference/artifacts/run-results-json) specifications is supported.

## Contribution

Development of this fork was partially sponsored by EPAM Systems Inc. https://www.epam.com/  

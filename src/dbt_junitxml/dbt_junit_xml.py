from junit_xml import TestSuite, TestCase, decode
import xml.etree.ElementTree as ET


class DBTTestCase(TestCase):
    """A JUnit test case with a result and possibly some stdout or stderr"""

    def __init__(
            self,
            name,
            classname=None,
            elapsed_sec=None,
            stdout=None,
            stderr=None,
            assertions=None,
            timestamp=None,
            status=None,
            category=None,
            file=None,
            line=None,
            log=None,
            url=None,
            allow_multiple_subelements=False,
    ):
        self.name = name
        self.assertions = assertions
        self.elapsed_sec = elapsed_sec
        self.timestamp = timestamp
        self.classname = classname
        self.status = status
        self.category = category
        self.file = file
        self.line = line
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr

        self.is_enabled = True
        self.errors = []
        self.failures = []
        self.skipped = []
        self.allow_multiple_subalements = allow_multiple_subelements


class DBTTestSuite(TestSuite):
    def __init__(self,
                 name,
                 test_cases=None,
                 hostname=None,
                 id=None,
                 package=None,
                 timestamp=None,
                 properties=None,
                 file=None,
                 log=None,
                 url=None,
                 stdout=None,
                 stderr=None,
                 time=None):
        super(DBTTestSuite, self).__init__(name,
                                           test_cases=None,
                                           hostname=None,
                                           id=None,
                                           package=None,
                                           timestamp=None,
                                           properties=None,
                                           file=None,
                                           log=None,
                                           url=None,
                                           stdout=None,
                                           stderr=None)
        self.name = name
        if not test_cases:
            test_cases = []
        try:
            iter(test_cases)
        except TypeError:
            raise TypeError("test_cases must be a list of test cases")
        self.test_cases = test_cases
        self.timestamp = timestamp
        self.hostname = hostname
        self.id = id
        self.package = package
        self.file = file
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr
        self.properties = properties
        self.time = time

    def build_xml_doc(self, encoding=None):
        super(DBTTestSuite, self).build_xml_doc(encoding=None)
        """
        Builds the XML document for the JUnit test suite.
        Produces clean unicode strings and decodes non-unicode with the help of encoding.
        @param encoding: Used to decode encoded strings.
        @return: XML document with unicode string elements
        """

        # build the test suite element
        test_suite_attributes = dict()
        if any(c.assertions for c in self.test_cases):
            test_suite_attributes["assertions"] = str(
                sum([int(c.assertions) for c in self.test_cases if c.assertions]))
        test_suite_attributes["disabled"] = str(
            len([c for c in self.test_cases if not c.is_enabled]))
        test_suite_attributes["errors"] = str(len([c for c in self.test_cases if c.is_error()]))
        test_suite_attributes["failures"] = str(len([c for c in self.test_cases if c.is_failure()]))
        test_suite_attributes["name"] = decode(self.name, encoding)
        test_suite_attributes["skipped"] = str(len([c for c in self.test_cases if c.is_skipped()]))
        test_suite_attributes["tests"] = str(len(self.test_cases))
        test_suite_attributes["time"] = str(
            sum(c.elapsed_sec for c in self.test_cases if c.elapsed_sec))

        if self.hostname:
            test_suite_attributes["hostname"] = decode(self.hostname, encoding)
        if self.id:
            test_suite_attributes["id"] = decode(self.id, encoding)
        if self.package:
            test_suite_attributes["package"] = decode(self.package, encoding)
        if self.timestamp:
            test_suite_attributes["timestamp"] = decode(self.timestamp, encoding)
        if self.file:
            test_suite_attributes["file"] = decode(self.file, encoding)
        if self.log:
            test_suite_attributes["log"] = decode(self.log, encoding)
        if self.url:
            test_suite_attributes["url"] = decode(self.url, encoding)
        if self.time:
            test_suite_attributes["time"] = decode(self.time, encoding)

        xml_element = ET.Element("testsuite", test_suite_attributes)

        # add any properties
        if self.properties:
            props_element = ET.SubElement(xml_element, "properties")
            for k, v in self.properties.items():
                attrs = {"name": decode(k, encoding), "value": decode(v, encoding)}
                ET.SubElement(props_element, "property", attrs)

        # add test suite stdout
        if self.stdout:
            stdout_element = ET.SubElement(xml_element, "system-out")
            stdout_element.text = decode(self.stdout, encoding)

        # add test suite stderr
        if self.stderr:
            stderr_element = ET.SubElement(xml_element, "system-err")
            stderr_element.text = decode(self.stderr, encoding)

        # test cases
        for case in self.test_cases:
            test_case_attributes = dict()
            test_case_attributes["name"] = decode(case.name, encoding)
            if case.assertions:
                # Number of assertions in the test case
                test_case_attributes["assertions"] = "%d" % case.assertions
            if case.elapsed_sec:
                test_case_attributes["time"] = "%f" % case.elapsed_sec
            if case.timestamp:
                test_case_attributes["timestamp"] = decode(case.timestamp, encoding)
            if case.classname:
                test_case_attributes["classname"] = decode(case.classname, encoding)
            if case.status:
                test_case_attributes["status"] = decode(case.status, encoding)
            if case.category:
                test_case_attributes["class"] = decode(case.category, encoding)
            if case.file:
                test_case_attributes["file"] = decode(case.file, encoding)
            if case.line:
                test_case_attributes["line"] = decode(case.line, encoding)
            if case.log:
                test_case_attributes["log"] = decode(case.log, encoding)
            if case.url:
                test_case_attributes["url"] = decode(case.url, encoding)

            test_case_element = ET.SubElement(xml_element, "testcase", test_case_attributes)

            # failures
            for failure in case.failures:
                if failure["output"] or failure["message"]:
                    attrs = {"type": "failure"}
                    if failure["message"]:
                        attrs["message"] = decode(failure["message"], encoding)
                    if failure["type"]:
                        attrs["type"] = decode(failure["type"], encoding)
                    failure_element = ET.Element("failure", attrs)
                    if failure["output"]:
                        failure_element.text = decode(failure["output"], encoding)
                    test_case_element.append(failure_element)

            # errors
            for error in case.errors:
                if error["message"] or error["output"]:
                    attrs = {"type": "error"}
                    if error["message"]:
                        attrs["message"] = decode(error["message"], encoding)
                    if error["type"]:
                        attrs["type"] = decode(error["type"], encoding)
                    error_element = ET.Element("error", attrs)
                    if error["output"]:
                        error_element.text = decode(error["output"], encoding)
                    test_case_element.append(error_element)

            # skipped
            for skipped in case.skipped:
                attrs = {"type": "skipped"}
                if skipped["message"]:
                    attrs["message"] = decode(skipped["message"], encoding)
                skipped_element = ET.Element("skipped", attrs)
                if skipped["output"]:
                    skipped_element.text = decode(skipped["output"], encoding)
                test_case_element.append(skipped_element)

            # test stdout
            if case.stdout:
                stdout_element = ET.Element("system-out")
                stdout_element.text = decode(case.stdout, encoding)
                test_case_element.append(stdout_element)

            # test stderr
            if case.stderr:
                stderr_element = ET.Element("system-err")
                stderr_element.text = decode(case.stderr, encoding)
                test_case_element.append(stderr_element)

        return xml_element

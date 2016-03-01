All Tests are divided into Test Files
- Each Test File contain tests for particular feature and comprises of multiple Test Classes
- Each Test Class contain tests for particular sub-feature and comprises of multiple Test Cases
- Each Test case tests a particular test :P

To Run all Tests:
 python -m unittest discover (better implementation)
 or
 python -m unittest discover tests "*.py"

To Run Individual tests:
 python -m unittest tests.tests_connection
 python -m unittest tests.tests_login
 python -m unittest tests.tests_query

To Run Individual testcases:
 (By Test Class)
 python -m unittest tests.tests_connection.BasicConnectionTestCase

 (By Test Case)
 python -m unittest tests.tests_connection.BasicConnectionTestCase.test_index 
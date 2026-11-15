# STQA test plan and traceability

## Objective and scope

Verify that the CovidCare learning portal implements the modules named by the project report: registration/login, report search/download, state dashboard, admin access, comments, next-day test-slot booking, and regex-oriented input validation. Testing uses black-box functional and validation techniques; Selenium WebDriver drives Chrome and TestNG reports results.

## Test cases

| ID | Module / technique | Scenario | Expected result | Automation |
|---|---|---|---|---|
| TC-01 | Home / functional | Open home and navigate to dashboard | Home loads and state data is displayed | Selenium/TestNG |
| TC-02 | Registration / boundary | Submit a 5-digit phone | Browser rejects the value against the 10-digit pattern | Selenium/TestNG |
| TC-03 | Registration / positive | Create a new account with valid email, 10-digit phone, and strong password; sign in | Account is stored and authenticated | Selenium/TestNG |
| TC-04 | Search / access control | Open report search signed out | Sign-in prompt is shown; results are not exposed | Selenium/TestNG |
| TC-05 | Admin / negative | Submit incorrect admin password | Error appears and admin page is not granted | Selenium/TestNG |
| TC-06 | Admin / positive | Sign in with configured admin credentials | Admin report list and seeded sample report appear | Selenium/TestNG |
| TC-07 | Registration / server validation | malformed email, phone, and weak password | Invalid formats are rejected by server validation helpers | PHP CLI unit tests |
| TC-08 | Reports / functional | Signed-in search by order number, patient name, and phone; download CSV | Matching report appears and CSV contains the report fields | Manual/API follow-up |
| TC-09 | Appointment / boundary | Test today, malformed date, invalid calendar date, and tomorrow | Only valid dates on or after tomorrow are accepted | PHP CLI unit tests |
| TC-10 | Comments / access | Post as signed-in user and attempt signed-out access | Valid comment is escaped and stored; anonymous submission redirects to login | Manual/API follow-up |
| TC-11 | Security / integration | Missing or altered CSRF token; SQL metacharacters in search | Request rejected or treated as data; no query manipulation | Manual/API follow-up |
| TC-12 | Regression / responsive | Check core views at desktop and narrow viewport | Navigation and content remain usable | Manual |

The report contains inconsistent totals (7 planned versus 9 pass/fail results and 2 versus 1 regex tests). This repository makes no claim about those prior execution counts. Run the included suite to obtain actual current results; rows marked manual/API follow-up remain pending automation.

## Test environment

PHP 8.2+, MySQL 8, Java 17+, Maven 3.8+, Selenium 4.24, TestNG 7.10.2, and Chrome/Chromium. PHP validation tests run with `php tests/php/ValidationTest.php`. Browser tests use Selenium Manager and headless Chrome by default.

## Defect reporting fields

Record test-case ID, build/commit, environment, preconditions, steps, expected result, actual result, severity, screenshot/log, and status (open/closed/retest). Maven Surefire/TestNG reports are written under `target/surefire-reports/`.

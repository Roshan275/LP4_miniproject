# CovidCare — STQA Mini Project

A COVID-19 information and testing portal built as a Software Testing and Quality Assurance (STQA) mini project. It covers registration and sign-in, report search and CSV download, a statewise dashboard, administrator access, community comments, and test-slot date validation. Selenium WebDriver with TestNG automates browser scenarios; PHP validation checks cover regex and date boundaries.

The report's state totals and sample reports are fictional seeded data for demonstration. This project is not for real patient information or production deployment.

## Requirements on Windows

- Windows 10 or 11
- PHP 8.2 or newer CLI with `pdo_mysql` and `mbstring` enabled
- MySQL Server 8.0 or newer (8.4 LTS is suitable)
- JDK 17 or newer
- Apache Maven 3.8 or newer
- Google Chrome (for Selenium browser tests)
- Internet access for Maven dependencies and Selenium Manager's ChromeDriver download

### Install the tools

1. **PHP:** Download the Windows x64 Non Thread Safe ZIP from the [PHP for Windows downloads](https://windows.php.net/download/). Extract it to `C:\php`. Copy `php.ini-development` to `php.ini`. In `php.ini`, set `extension_dir = "ext"` and enable `extension=pdo_mysql` and `extension=mbstring` by removing the leading semicolon. Add `C:\php` to the Windows `Path` environment variable. If PHP reports a missing runtime DLL, install the Microsoft Visual C++ Redistributable linked from the PHP download page.
2. **MySQL:** Install MySQL Server using the [official MySQL Community Server downloads](https://dev.mysql.com/downloads/mysql/). The [Windows MSI installation guide](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html) walks through configuration. Set a root password and make sure the MySQL Windows service is running. Add the MySQL `bin` directory to `Path` (the default for 8.4 is `C:\Program Files\MySQL\MySQL Server 8.4\bin`).
3. **Java:** Install a JDK 17+ distribution, such as [Eclipse Temurin](https://adoptium.net/temurin/releases/). Set `JAVA_HOME` to its JDK folder and add `%JAVA_HOME%\bin` to `Path`.
4. **Maven:** Download the binary ZIP from [Apache Maven](https://maven.apache.org/download.cgi), extract it (for example, to `C:\apache-maven`), and add its `bin` folder to `Path`.
5. **Chrome:** Install [Google Chrome](https://www.google.com/chrome/). Selenium Manager obtains a compatible ChromeDriver when the browser tests start.

Open a **new Command Prompt** after changing `Path`, then verify the tools:

```bat
php -v
php -m | findstr /I "mbstring PDO pdo_mysql"
mysql --version
java -version
mvn -version
```

The PHP modules command should list `mbstring`, `PDO`, and `pdo_mysql`. Maven should be 3.8 or newer. The project compiles its Selenium tests for Java 17, so newer JDKs also work.

> XAMPP is an alternative way to get PHP on Windows, but current XAMPP packages ship MariaDB rather than MySQL. If you use XAMPP for PHP, use its `C:\xampp\php` in `Path` and install/run MySQL Server separately to match the project setup. Do not start both database servers on port 3306.

## Set up and run the app

Use **Command Prompt** for these commands. Replace the example folder with wherever you downloaded/cloned this project:

```bat
cd /d C:\path\to\covid-stqa-project
copy .env.example .env
notepad .env
```

In `.env`, set `DB_USER=root`, `DB_PASSWORD` to the MySQL root password, and choose local `ADMIN_EMAIL` and `ADMIN_PASSWORD` values. Keep `.env` private; Git ignores it.

With the MySQL service running, create the database and sample records:

```bat
mysql -u root -p < database\schema.sql
```

Enter the MySQL password when prompted. Start the PHP server in this Command Prompt:

```bat
php -S 127.0.0.1:8000 -t public
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Register a user to try sign-in, comments, report search, and test-slot requests. Sample report order number: `COVID-2026-0001`; mobile number: `9876543210`.

## Run the STQA tests

Keep the PHP server running. Open a **second Command Prompt**, set the project directory again, then run the PHP validation checks and browser tests:

```bat
cd /d C:\path\to\covid-stqa-project
php tests\php\ValidationTest.php
mvn test -DbaseUrl=http://127.0.0.1:8000
```

The Selenium suite uses headless Chrome. Maven downloads dependencies on its first run. TestNG/Surefire reports are saved under `target\surefire-reports\`. CI runs these same validation and browser checks on pushes and pull requests.

For expected behavior and test-case traceability, see [docs/TEST-PLAN.md](docs/TEST-PLAN.md).

## Push to GitHub

This project is intended to live as a folder in the `LP4_miniproject` repository. From the repository root, stage and commit the STQA folder and the repository README update, then push the `main` branch:

```bat
git add README.md covid-stqa-project
git commit -m "Add CovidCare STQA mini project"
git push origin main
```

Never commit `.env`, real patient information, passwords, or API keys.

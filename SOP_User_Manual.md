# QualiX Standard Operating Procedure (SOP) & User Manual
### HDFC Bank Enterprise Data Quality & Validation Platform

Welcome to the **QualiX User Manual**. This document serves as a step-by-step Standard Operating Procedure (SOP) to help business users, data analysts, and administrators perform data quality checks and comparisons.

QualiX allows you to connect to enterprise data sources, map columns between a source and a target table, validate data using predefined rules, and automate these validations using schedules or database events.

---

## Table of Contents
1. [Overview and Access Control](#1-overview-and-access-control)
2. [Step 1: Managing Data Connections](#2-step-1-managing-data-connections)
3. [Step 2: Creating Projects and Pipelines (Mappings)](#3-step-2-creating-projects-and-pipelines-mappings)
4. [Step 3: Dictionary of Data Quality Validation Rules](#4-step-3-dictionary-of-data-quality-validation-rules)
5. [Step 4: Running Validations and Reviewing Reports](#5-step-4-running-validations-and-reviewing-reports)
6. [Step 5: Scheduling and Automating Workflows](#6-step-5-scheduling-and-automating-workflows)
7. [Step 6: Setting Up DB Triggers (High Water Mark Polling)](#7-step-6-setting-up-db-triggers-high-water-mark-polling)
8. [Dashboard, Auditing, and Help Center](#8-dashboard-auditing-and-help-center)

---

## 1. Overview and Access Control

### 1.1 What is QualiX?
QualiX is an enterprise-grade platform designed to compare data between a **Source** (where data starts, e.g., a raw database or CSV file) and a **Target** (where data lands, e.g., an Oracle database or Databricks data lakehouse). It ensures that data has been loaded accurately without corruption, truncation, missing records, or formatting shifts.

### 1.2 User Roles & Permissions
Your login profile is assigned one of three security roles, which dictates what actions you can perform:

| Role | Permissions | Best For |
| :--- | :--- | :--- |
| **Admin** | Full access to manage users, database connections, pipelines, validation runs, scheduled workflows, and view all system-wide logs. | Platform administrators, lead engineers. |
| **Contributor** | Can create connections, build pipelines (mappings), and manually run validations. *Cannot manage users or access system admin settings.* | Data analysts, ETL developers, QA testers. |
| **Auditor** | Read-only access. Can view dashboards, look at configuration mappings, read validation reports, and review logs. *Cannot create, edit, or execute anything.* | Business owners, compliance officers, risk managers. |

### 1.3 How to Log In
1. Open the QualiX URL in your browser (you will be automatically redirected to `/accounts/login/`).
2. Enter your credentials. 
3. *Note for HDFC internal users:* If your account is integrated with Active Directory, check the **LDAP login** toggle to authenticate using your standard Windows/corporate credentials.
4. If you forget your password, click **Forgot Password** on the login screen to receive a reset link.

---

## 2. Step 1: Managing Data Connections

Before comparing any data, you must connect QualiX to your data storage systems. QualiX supports databases, data lakehouses, and files.

### 2.1 Supported Connection Types
* **Databases**: PostgreSQL, MySQL, Databricks, DB2, Oracle, and Lakehouse (SQL based).
* **Flat Files**: CSV, Parquet, Excel (`.xlsx`), and Plain Text.

### 2.2 Adding a New Connection
1. Navigate to **Connections** from the left sidebar and click **Add Connection** (or **Create New**).
2. Enter a **Friendly Name** (e.g., `Core_Banking_Postgres_Prod`).
3. Select the **Connection Type** from the dropdown.
4. **For Database Connections**:
   - Fill in the **Host** IP address or domain name.
   - Enter the **Port** number (defaults are populated, e.g., 5432 for PostgreSQL, 1521 for Oracle).
   - Enter the **Database Name**.
   - Provide the **Username** and **Password** (passwords are automatically encrypted at rest using secure AES-256 standard key encryption).
   - *Optional:* If a custom database driver is required, specify the driver name (e.g., `oracledb` or `pyodbc`).
5. **For File Connections**:
   - Upload the sample file (CSV, Parquet, Excel, or Text) using the file uploader. QualiX stores the schema structure of this file for mapping purposes.
6. Click **Test Connection** before saving. 
   - A notification toast will display `Success` or `Failed` along with the exact connection error message to help you debug credentials/network blocks.
7. If the test is successful, click **Save**.

---

## 3. Step 2: Creating Projects and Pipelines (Mappings)

Once your connections are set up, you define a **Pipeline (Mapping)**. A pipeline represents the instruction to compare one specific source table/file against a target table/file.

### 3.1 Creating a Project Group
Pipelines are organized inside **Projects** to keep your workspace tidy.
1. Go to **Pipelines/Mappings** on the sidebar.
2. Click **Create Project**.
3. Provide a name (e.g., `Retail_Loans_ETL`) and an optional description, then click **Save**.

### 3.2 Building a Pipeline (Mapping)
1. Go to the project dashboard and click **Create Pipeline** (or **Create Mapping**).
2. Enter a **Pipeline Name** (e.g., `Customer_Master_Validation`).
3. **Choose Source Details**:
   - Select the **Source Connection** you created in Step 1.
   - For databases, QualiX will automatically load lists of **Catalogs**, **Schemas**, and **Tables**. Select the appropriate catalog, schema, and table.
4. **Choose Target Details**:
   - Select the **Target Connection**.
   - Select the target catalog, schema, and table.
5. **Configure Date Filters (Optional)**:
   If your tables are huge, you should filter them by date (e.g., only validating today's records) to keep runs fast.
   - **No Filter**: Validates the entire table.
   - **Specific Date**: Filter records matching a specific date (e.g. `2026-07-27`).
   - **Date Range**: Filter records between a Start Date and an End Date.
   - *Pro Tip:* You can apply a **Shared Date Filter** (same filter on both tables) or click **Separate Date Filters** if your source and target tables store date metadata in different columns or formats.
6. **Save Draft Feature**:
   - If you are building a complex pipeline with dozens of columns and get interrupted, QualiX **automatically saves your progress as a draft**. 
   - When you return to the page, a popup will ask if you want to restore your draft, ensuring you never lose your progress!

### 3.3 Mapping Columns & Selecting Rules
1. After specifying the source and target tables, click **Fetch Schema** or **Proceed to Columns**.
2. QualiX will load all columns from the source on the left and target on the right.
3. Map each source column to its corresponding target column by matching them.
4. For each mapped column pair, **select the check box of validation operations** you want to run (e.g., checking if the minimum value, sum, or null counts match). Refer to Section 4 for details on rules.
5. Click **Create Mapping** (or **Save Pipeline**).

---

## 4. Dictionary of Data Quality Validation Rules

When mapping columns, you specify rules to apply. These rules compare aggregate stats or formatting between the source and target.

### 4.1 String (Text) Columns
* **Null Check**: Counts the missing/blank values. A match means both tables have the exact same number of missing values.
* **Length Check / Sum Length**: Adds up the length (character count) of all text rows in the column. Useful to detect text truncation.
* **Trim Check**: Checks for leading/trailing spaces. Mismatch indicates that one table has extra trailing spaces (e.g., `'John '` vs `'John'`).
* **Case Insensitive Check**: Converts text to lowercase and strips space variations before comparing. Helps identify if casing differs (e.g. `'HDFC'` vs `'hdfc'`).
* **Contains Check**: Counts how many rows contain a specific word or letter snippet.
* **Regex Check / Pattern Match**: Validates text structures against standard patterns (like validating email addresses or phone number formats).
* **Hash Validation**: Generates a fast mathematical fingerprint of the column values. If they don't match, at least one row has different text.

### 4.2 Numeric (Integer and Float) Columns
* **Row Count Match**: Compares the total row count (number of rows) of the tables. Highly recommended as a base check.
* **Count**: Counts the number of non-empty numbers in the column.
* **Distinct Count**: Counts unique values. Useful for checking primary keys or unique IDs.
* **Min Value Check**: Finds the smallest number. Mismatches highlight data truncation or incorrect bounds.
* **Max Value Check**: Finds the largest number.
* **Sum Check**: Adds all numbers in the column together. Ideal for financial columns (like transaction amounts).
* **Average Check**: Calculates the average value.
* **Range Check**: Counts how many numbers fall within a specific range (e.g., between 0 and 100).

### 4.3 Date and Time Columns
* **Min Date**: Finds the oldest date in the column.
* **Max Date**: Finds the newest date in the column.
* **Null Check**: Counts missing dates.
* **Distinct Count**: Counts the unique dates present.

---

## 5. Step 4: Running Validations and Reviewing Reports

Once a Pipeline (Mapping) is configured, you can execute validations to verify data quality.

### 5.1 Manual Execution
* **Quick Validate**: Under the **Validations** tab, you can click "Quick Validate". Select your pipeline and run it instantly.
* **Pipeline Run**: Go to **Pipelines**, click your pipeline's name, and click the **Run Now** button.

### 5.2 Monitoring Live Runs
1. Once triggered, QualiX redirects you to the **Validation Progress** page.
2. A live progress bar will advance from **0% to 100%** as it queries the databases.
3. If an error occurs (e.g. database goes offline), the status will change to **Failed** and show the error message.

### 5.3 Reviewing the Report
Once completed, the page displays a comprehensive audit report:
* **Execution Summary**: Shows Run ID, Execution Time, Triggered By user, columns validated, and the Date Filters applied.
* **KPI Metrics**: 
  - **Pass Rate**: The percentage of rules that matched successfully.
  - **Passed Checks**: Total rules that matched.
  - **Failed Checks**: Total rules that mismatched.
* **Detailed Rules Grid**:
  - Displays each column, the rule applied (e.g., `Sum`), the source value, the target value, and the status (**MATCH** in green, or **MISMATCH** in red).
  - Shows the **Difference** value (e.g., if source sum is `10,000` and target sum is `9,950`, difference is `-50`).

### 5.4 Exporting Reports
Click the **Export Report** button at the top right of any completed run to download a beautifully formatted Microsoft Excel (`.xlsx`) sheet:
1. **Sheet 1: Validation Report**: Contains a grid of every column checked, the rule name, source value, target value, Match/Mismatch label (color-coded green/red), and the calculated difference.
2. **Sheet 2: Report Narrative**: A high-level audit summary containing the metadata of the execution: Run ID, execution date, who triggered it, overall status, and database configurations.

---

## 6. Step 5: Scheduling and Automating Workflows

To run validations automatically every day, week, or month, use **Workflows**.

### 6.1 Creating a Workflow
1. Go to **Workflows** in the sidebar.
2. Click **Create Workflow** (or **Add Workflow**).
3. Provide a **Workflow Name** (e.g., `Daily_EOD_Loans_Validation`).
4. Select the **Pipeline/Mapping** that this workflow should run.
5. Select a **Schedule Type**:
   - **On Demand**: Only runs when you manually click trigger.
   - **Daily**: Runs every day at a specific time (e.g., `21:30`).
   - **Weekly**: Runs on a specific day of the week (e.g., every Monday) at a specific time.
   - **Monthly**: Runs on a specific date of the month (e.g., the 1st of every month).
   - **DB Trigger**: (See Section 7 for details).
6. **Configure Email Notifications**:
   - Enter a **Recipient Email** address.
   - Upon completion, QualiX will automatically email the detailed Excel report to this address, stating whether the run passed or failed.
7. Click **Create Workflow**.

### 6.2 Managing Workflows
* **Toggle Active/Inactive**: In the Workflows list, use the toggle switch to enable/disable a workflow. Inactive workflows will not run on their schedules.
* **Manual Override**: Even if scheduled, you can click **Run Now** next to a workflow to trigger it immediately.

---

## 7. Step 6: Setting Up DB Triggers (High Water Mark Polling)

Instead of running a workflow at a fixed clock time, you can schedule it to run **immediately after your ETL (data loading) finishes**. QualiX achieves this by checking a standard tracking table named `hwm_chk` (High Water Mark Check) in your database.

### 7.1 How DB Trigger Polling Works
When a workflow is set to "DB Trigger", it does not run immediately.
1. At the configured **Trigger Scheduled Time**, QualiX transitions the workflow status to **Polling**.
2. QualiX executes a query every **60 seconds** looking for a signal:
   ```sql
   SELECT COUNT(*) FROM hwm_chk
   WHERE trigger_name = '<your_trigger_name>'
     AND hwm_flag = 'Y'
     AND etl_date = CURRENT_DATE;
   ```
3. Once the ETL system completes, it must write a row into the `hwm_chk` table indicating completion:
   - `trigger_name` = (Matches the name configured in the workflow)
   - `hwm_flag` = `'Y'`
   - `etl_date` = Today's date
4. When QualiX finds this row (count > 0), the status updates to **Triggered**, polling stops, and the data validation starts immediately.
5. If no row is found within the **Poll Duration (Hours)** limit (e.g., 3 hours), QualiX stops polling, flags the run status as **Timeout**, and sends an email warning.

### 7.2 Configuring a DB Trigger Workflow
1. Create or edit a Workflow.
2. Set **Schedule Type** to **DB Trigger**.
3. Fill in the DB Trigger specific parameters:
   - **Trigger Name**: The text ID of the loader task (e.g., `load_retail_loans_prod`). This must match the `trigger_name` column in `hwm_chk`.
   - **Trigger Scheduled Time**: The clock time to start looking for the ETL flag (e.g., `04:00 AM`).
   - **Poll Duration (Hours)**: The maximum hours to wait before giving up (e.g., `4` hours).
4. Save the workflow.
5. In the workflows overview list, click **Start Polling** to put the engine into active polling mode.

---

## 8. Dashboard, Auditing, and Help Center

### 8.1 Dashboard Metrics
The home page provides an executive summary:
* **Total Connections, Pipelines, & Active Workflows**: Quick counts.
* **Validation Success Rate**: A donut chart illustrating completed vs. failed validation runs.
* **Recent Activity Log**: An interactive timeline of validation runs.
* **System Notifications**: Click the bell icon in the top header to view unread alerts (such as completed or failed runs). Click **Clear All** to dismiss.

### 8.2 Audit Logs
Every user interaction (logging in, creating pipelines, modifying connections, running reports) is recorded in the **Logs** tab. This allows compliance auditors to review historical configuration changes and see who executed what data verification.

### 8.3 In-App Help Center
If you are confused about how a specific validation rule calculates its results:
1. Click **Help Center** (or go to `/help/` in the sidebar).
2. Choose a tab based on your column type: **String**, **Integer**, **Float**, or **Date**.
3. Use the search bar to query operations (e.g. search "trim" or "regex").
4. The system will display:
   - **Name and Alias** of the check.
   - **Underlying Logic** of how it computes metrics.
   - **What constitutes a Match** vs. a **Mismatch**.

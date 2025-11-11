<img alt="gitleaks badge" src="https://img.shields.io/badge/protected%20by-gitleaks-blue"> ![Static Badge](https://img.shields.io/badge/Devops-Deepak%20Venkatram-Green)

🛡️ AWS IAM User Management Toolkit

A complete Python-based toolkit for auditing, reviewing, and managing AWS IAM users at scale.

When your AWS account grows and you have **dozens or hundreds of IAM users**, managing them manually through the AWS Console becomes inefficient and error-prone.
This toolkit lets you **export all IAM users and their permissions into Excel**, review or modify them offline, and **apply changes automatically** — all from Python.

🚀 Features

🔍 Export all IAM users to Excel with full details:

* User IDs, creation date, MFA status, console access
* Groups and attached policies
* Access keys and last usage
* **Last console login and password usage** (from AWS Credential Report)
* 📊 Human-readable Excel report for offline review or compliance audit
* 🧾 Editable “Action” columns to define role or permission changes
* ⚙️ Apply changes automatically from the Excel file
* 🧠 Supports sandbox and production AWS profiles for safe testing

📂 Repository Structure

aws-iam-user-management/
│
├── export_iam_users_with_login_activity.py   # Export IAM users and activity to Excel
├── apply_iam_user_changes.py                 # Apply IAM changes from Excel
├── requirements.txt                          # Python dependencies
└── README.md                                 # This documentation

🧰 Prerequisites

1. AWS Account (with IAM access)
2. IAM permissions to manage users:

   iam:ListUsers
   iam:GetUser
   iam:ListGroupsForUser
   iam:ListAttachedUserPolicies
   iam:ListUserPolicies
   iam:GetLoginProfile
   iam:ListAccessKeys
   iam:GetAccessKeyLastUsed
   iam:GenerateCredentialReport
   iam:GetCredentialReport
   ```
3. Python 3.8+
4. AWS CLI configured

Bash

aws configure --profile my-profile

5. Install dependencies:

Bash
pip install boto3 pandas openpyxl


⚙️ Setup

1️⃣ Clone the repository

Bash
git clone https://github.com/<yourusername>/aws-iam-user-management.git
cd aws-iam-user-management


2️⃣ Configure your AWS CLI

If you want to use a sandbox account for safe testing:

Bash
aws configure --profile sandbox

Then your Python scripts can use it:

python
session = boto3.Session(profile_name='sandbox')
iam = session.client('iam')

📊 Step 1: Export IAM Users & Details

Run:

Bash
python export_iam_users_with_login_activity.py

This will generate a detailed Excel file:

iam_user_roles_with_activity.xlsx

Example output columns:

| UserName | ConsoleAccess | MFAEnabled | Groups     | AttachedPolicies    | PasswordLastUsed | AccessKey1LastUsed | Action        | NewGroups  | NewPolicies     |
| -------- | ------------- | ---------- | ---------- | ------------------- | ---------------- | ------------------ | ------------- | ---------- | --------------- |
| alice    | TRUE          | TRUE       | Admins     | AdministratorAccess | 2025-11-01       | 2025-10-30         | change_groups | Developers |                 |
| bob      | FALSE         | FALSE      | Developers | ReadOnlyAccess      | N/A              | N/A                | add_policy    |            | PowerUserAccess |

✏️ Step 2: Review & Edit the Excel File

Once the Excel file is generated:

1. Open `iam_user_roles_with_activity.xlsx`.

2. Review each user’s:

   * LastConsoleLogin / PasswordLastUsed → helps identify inactive users.
   * MFAEnabled → check for security compliance.
   * Groups / AttachedPolicies → see current access levels.

3. In the Action column, specify what to do:

   | Action          | Description                      |
   | --------------- | -------------------------------- |
   | `add_group`     | Add user to new groups           |
   | `remove_group`  | Remove user from groups          |
   | `change_groups` | Replace all groups with new ones |
   | `add_policy`    | Attach new managed policies      |
   | `remove_policy` | Detach existing policies         |
   | `deactivate`    | Deactivate user’s access keys    |
   | `delete`        | Remove the user completely       |

4. Fill NewGroups and/or NewPolicies as comma-separated lists.

🧠 Example:

| UserName | Action        | NewGroups  | NewPolicies     |
| -------- | ------------- | ---------- | --------------- |
| alice    | change_groups | Developers |                 |
| bob      | add_policy    |            | PowerUserAccess |

🧩 Step 3: Apply Changes

Once you’ve reviewed and updated the Excel file:

Run:

python apply_iam_user_changes.py


This script will:

* Read the Excel file.
* Perform each specified action on the target IAM user.
* Print progress and confirmation messages in the terminal.

Example output:

🔹 Processing user: alice | Action: change_groups
  - Removed from Admins
  + Added to Developers
🔹 Processing user: bob | Action: add_policy
  + Attached policy PowerUserAccess
✅ Finished applying IAM changes.

🧠 Where This Toolkit Helps

| Scenario                           | How It Helps                                                    |
| ---------------------------------- | --------------------------------------------------------------- |
| Large AWS accounts (10+ users)     | Quickly audit all IAM users and permissions in one view.        |
| Security audits                    | Identify inactive, non-MFA users and risky access patterns.     |
| Least privilege enforcement        | Downgrade or remove over-privileged users.                      |
| Automation & DevOps                | Integrate IAM user cleanup into CI/CD or maintenance pipelines. |
| Governance compliance              | Generate reports for SOC2, ISO 27001, or internal audits.       |

🔒 Best Practices

* Always test first in a sandbox AWS account.
* Use groups instead of assigning direct policies to users.
* Rotate and disable stale access keys regularly.
* Keep MFA enabled for all console users.
* Consider using AWS IAM Identity Center (SSO) for large orgs.

🧱 Example Workflow (for 50+ users)

1. Export user list:

Bash
AWS_PROFILE=production python export_iam_users_with_login_activity.py

2. Review Excel for inactive or risky users.
3. Mark users with `Action = deactivate` or `change_groups`.
4. Apply safely:

Bash
AWS_PROFILE=production python apply_iam_user_changes.py

5. Re-run export to confirm changes.

🧰 Future Enhancements (ideas)

* 📅 Add automatic `LastActivityDays` calculation for quick filtering.
* 📬 Email report summaries to administrators.
* 🚨 Detect and flag inactive users automatically.
* ☁️ Integrate with AWS Organizations for multi-account management.

🧑‍💻 Contributing

Pull requests and feature suggestions are welcome!
If you add support for organizations, SSO, or CloudTrail-based activity tracking, please open a PR.

⚠️ Disclaimer

This tool modifies IAM users and policies — test thoroughly in a non-production account first.
Use with caution and appropriate IAM permissions.
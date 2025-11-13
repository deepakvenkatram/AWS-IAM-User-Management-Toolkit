"""
===============================================================================
AWS IAM User Export Tool
Maintainer: Deepak Venkatram
===============================================================================

Description:
------------
This script automates the process of auditing IAM users in an AWS account.
It performs the following key tasks:

1. Generates and downloads the latest IAM Credential Report.
2. Merges credential data with IAM user details, including:
   - Groups and attached managed policies
   - MFA status and console access
   - Access keys and their last usage
   - Password and last console login information
3. Exports all collected information into a structured Excel file
   for easy offline review, compliance checks, and permission analysis.

Use Case:
---------
Ideal for AWS environments with multiple IAM users where managing users
via the AWS Management Console is inefficient. This tool provides a 
comprehensive, spreadsheet-based view to help identify inactive users,
review permissions, and enforce least-privilege best practices.

Output:
-------
Generates an Excel report named:
iam_user_roles_with_activity.xlsx

Example:
--------
python export_iam_users_with_login_activity.py

===============================================================================
"""

import boto3
import pandas as pd
from io import BytesIO
from datetime import datetime
import time

iam = boto3.client('iam')


def get_credential_report():
    """
    Generate and download the IAM credential report.
    Returns a pandas DataFrame.
    """
    print("📄 Generating IAM credential report...")
    # Generate report
    iam.generate_credential_report()

    # Wait for the report to complete
    print("⏳ Waiting for credential report to generate...")
    while True:
        try:
            report = iam.get_credential_report()
            # The report is ready if it has content or if the state is COMPLETE.
            if 'Content' in report or report.get('State') == 'COMPLETE':
                break
        except iam.exceptions.CredentialReportNotReadyException:
            # If the report is not ready, wait and try again.
            pass
        
        time.sleep(2)

    csv_data = report['Content']
    df = pd.read_csv(BytesIO(csv_data))
    print("✅ Credential report retrieved successfully.")
    return df


def get_user_details(user_name):
    """
    Collects IAM user details (groups, policies, MFA, etc.)
    """
    user = iam.get_user(UserName=user_name)['User']
    user_info = {
        'UserName': user_name,
        'UserId': user['UserId'],
        'Arn': user['Arn'],
        'CreateDate': user['CreateDate'],
    }

    # Console access
    try:
        iam.get_login_profile(UserName=user_name)
        user_info['ConsoleAccess'] = True
    except iam.exceptions.NoSuchEntityException:
        user_info['ConsoleAccess'] = False

    # MFA
    mfa = iam.list_mfa_devices(UserName=user_name)['MFADevices']
    user_info['MFAEnabled'] = len(mfa) > 0

    # Access keys
    keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
    user_info['AccessKeys'] = len(keys)
    user_info['ActiveKeys'] = sum(1 for k in keys if k['Status'] == 'Active')
    if keys:
        user_info['LastKeyUsed'] = iam.get_access_key_last_used(
            AccessKeyId=keys[0]['AccessKeyId']
        )['AccessKeyLastUsed'].get('LastUsedDate', 'Never')
    else:
        user_info['LastKeyUsed'] = 'No Keys'

    # Policies
    attached_policies = iam.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
    user_info['AttachedPolicies'] = ', '.join(p['PolicyName'] for p in attached_policies)

    # Groups
    groups = iam.list_groups_for_user(UserName=user_name)['Groups']
    user_info['Groups'] = ', '.join(g['GroupName'] for g in groups)

    # Placeholder columns for actions
    user_info['Action'] = ''
    user_info['NewGroups'] = ''
    user_info['NewPolicies'] = ''

    return user_info


def export_users_to_excel(filename='iam_user_roles_with_activity.xlsx'):
    """
    Combines IAM user data with credential report and exports to Excel.
    """
    print("📊 Collecting IAM user data...")

    # Fetch credential report
    cred_df = get_credential_report()

    # Map username → last login info
    cred_df = cred_df.rename(columns=lambda x: x.strip())
    cred_info = cred_df.set_index('user').to_dict(orient='index')

    all_details = []
    paginator = iam.get_paginator('list_users')

    for page in paginator.paginate():
        for user in page['Users']:
            user_name = user['UserName']
            details = get_user_details(user_name)

            # Merge credential report info
            if user_name in cred_info:
                c = cred_info[user_name]
                details['PasswordEnabled'] = c.get('password_enabled')
                details['PasswordLastUsed'] = c.get('password_last_used')
                details['PasswordLastChanged'] = c.get('password_last_changed')
                details['LastConsoleLogin'] = c.get('password_last_used')
                details['AccessKey1LastUsed'] = c.get('access_key_1_last_used_date')
                details['AccessKey2LastUsed'] = c.get('access_key_2_last_used_date')
            else:
                details['PasswordEnabled'] = None
                details['PasswordLastUsed'] = None
                details['PasswordLastChanged'] = None
                details['LastConsoleLogin'] = None
                details['AccessKey1LastUsed'] = None
                details['AccessKey2LastUsed'] = None

            all_details.append(details)

    df = pd.DataFrame(all_details)

    # Columns that may contain datetimes
    date_columns = [
        'CreateDate', 'LastKeyUsed', 'PasswordLastUsed', 'PasswordLastChanged',
        'LastConsoleLogin', 'AccessKey1LastUsed', 'AccessKey2LastUsed'
    ]

    for col in date_columns:
        if col in df.columns:
            # Convert column to datetime (UTC), coercing errors for non-date strings.
            # This standardizes all date-like values into a consistent format.
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
            
            # Remove the timezone to make it 'naive' for Excel compatibility.
            df[col] = df[col].dt.tz_localize(None)

    df.to_excel(filename, index=False)
    print(f"\n✅ Detailed IAM user report with login activity saved to: {filename}")


if __name__ == "__main__":
    export_users_to_excel()

import boto3
import pandas as pd

iam = boto3.client('iam')

def apply_changes(filename='iam_user_roles_report.xlsx'):
    df = pd.read_excel(filename)

    for _, row in df.iterrows():
        username = row['UserName']
        action = str(row.get('Action', '')).strip().lower()
        new_groups = [g.strip() for g in str(row.get('NewGroups', '')).split(',') if g.strip()]
        new_policies = [p.strip() for p in str(row.get('NewPolicies', '')).split(',') if p.strip()]

        if not action:
            continue

        print(f"\n🔹 Processing user: {username} | Action: {action}")

        try:
            if action == 'change_groups':
                # Remove all existing groups, then add new ones
                old_groups = iam.list_groups_for_user(UserName=username)['Groups']
                for g in old_groups:
                    iam.remove_user_from_group(UserName=username, GroupName=g['GroupName'])
                    print(f"  - Removed from {g['GroupName']}")
                for g in new_groups:
                    iam.add_user_to_group(UserName=username, GroupName=g)
                    print(f"  + Added to {g}")

            elif action == 'add_group':
                for g in new_groups:
                    iam.add_user_to_group(UserName=username, GroupName=g)
                    print(f"  + Added to {g}")

            elif action == 'remove_group':
                for g in new_groups:
                    iam.remove_user_from_group(UserName=username, GroupName=g)
                    print(f"  - Removed from {g}")

            elif action == 'add_policy':
                for p in new_policies:
                    arn = f"arn:aws:iam::aws:policy/{p}"
                    iam.attach_user_policy(UserName=username, PolicyArn=arn)
                    print(f"  + Attached policy {p}")

            elif action == 'remove_policy':
                for p in new_policies:
                    arn = f"arn:aws:iam::aws:policy/{p}"
                    iam.detach_user_policy(UserName=username, PolicyArn=arn)
                    print(f"  - Detached policy {p}")

            elif action == 'deactivate':
                keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
                for k in keys:
                    if k['Status'] == 'Active':
                        iam.update_access_key(UserName=username, AccessKeyId=k['AccessKeyId'], Status='Inactive')
                        print(f"  🔒 Deactivated key {k['AccessKeyId']}")

            elif action == 'delete':
                # Must detach policies and remove from groups first
                groups = iam.list_groups_for_user(UserName=username)['Groups']
                for g in groups:
                    iam.remove_user_from_group(UserName=username, GroupName=g['GroupName'])
                attached = iam.list_attached_user_policies(UserName=username)['AttachedPolicies']
                for p in attached:
                    iam.detach_user_policy(UserName=username, PolicyArn=p['PolicyArn'])
                iam.delete_user(UserName=username)
                print(f"  ❌ Deleted user {username}")

        except Exception as e:
            print(f"  ⚠️ Error processing {username}: {e}")

    print("\n✅ Finished applying IAM changes.")

if __name__ == "__main__":
    apply_changes()

"""
Deletes ALL users and their related data EXCEPT the admin user.
Run: python reset_users.py
"""
from app import create_app
from extensions import db
from models import (
    User, CompanyProfile, LandownerProfile, SubordinateProfile,
    VerificationTask, CarbonAssessment, CarbonCredit,
    EmissionReport, CarbonTransaction
)

app = create_app()

def reset_users():
    with app.app_context():
        # Get all non-admin user IDs
        non_admin_users = User.query.filter(User.role != 'admin').all()
        user_ids = [u.id for u in non_admin_users]

        if not user_ids:
            print("No non-admin users found. Nothing to delete.")
            return

        print(f"Found {len(user_ids)} non-admin users to delete.")
        print(f"Users: {[(u.username, u.role) for u in non_admin_users]}")
        
        confirm = input("\n⚠️  This will DELETE all data for these users. Type 'yes' to confirm: ")
        if confirm.strip().lower() != 'yes':
            print("Aborted.")
            return

        # Delete in reverse dependency order (child tables first)
        
        # 1. CarbonTransactions (depends on CompanyProfile, LandownerProfile, CarbonCredit)
        count = CarbonTransaction.query.delete()
        print(f"  Deleted {count} CarbonTransactions")

        # 2. CarbonCredits (depends on CarbonAssessment, User)
        count = CarbonCredit.query.filter(CarbonCredit.landowner_id.in_(user_ids)).delete()
        print(f"  Deleted {count} CarbonCredits")

        # 3. CarbonAssessments (depends on VerificationTask, User)
        count = CarbonAssessment.query.filter(CarbonAssessment.landowner_id.in_(user_ids)).delete()
        print(f"  Deleted {count} CarbonAssessments")

        # 4. EmissionReports (depends on VerificationTask, User)
        count = EmissionReport.query.filter(EmissionReport.company_id.in_(user_ids)).delete()
        print(f"  Deleted {count} EmissionReports")

        # 5. VerificationTasks (depends on User)
        count = VerificationTask.query.filter(VerificationTask.subordinate_id.in_(user_ids)).delete()
        print(f"  Deleted {count} VerificationTasks")

        # 6. Profiles (depend on User)
        count = CompanyProfile.query.filter(CompanyProfile.user_id.in_(user_ids)).delete()
        print(f"  Deleted {count} CompanyProfiles")

        count = LandownerProfile.query.filter(LandownerProfile.user_id.in_(user_ids)).delete()
        print(f"  Deleted {count} LandownerProfiles")

        count = SubordinateProfile.query.filter(SubordinateProfile.user_id.in_(user_ids)).delete()
        print(f"  Deleted {count} SubordinateProfiles")

        # 7. Finally, delete the Users themselves
        count = User.query.filter(User.role != 'admin').delete()
        print(f"  Deleted {count} Users")

        db.session.commit()
        print("\n✅ Done! Only admin user remains.")

        # Verify
        remaining = User.query.all()
        print(f"Remaining users: {[(u.username, u.role) for u in remaining]}")

if __name__ == '__main__':
    reset_users()

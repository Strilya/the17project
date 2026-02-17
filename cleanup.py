"""
Cleanup Utility - Remove all temp and test files
Run this to clean up the project
"""

import os
import glob
import shutil

def cleanup_project():
    """Clean up all temporary and test files"""

    print("=" * 70)
    print("THE17PROJECT - CLEANUP UTILITY")
    print("=" * 70)

    # Files and patterns to remove
    cleanup_items = {
        "Test files": [
            "test_*.py",
            "download_music.py"
        ],
        "Temp videos": [
            "output/temp_*.mp4",
            "output/*_slack.mp4",
            "src/output/*.mp4"
        ],
        "Temp audio": [
            "output/temp_*.mp3",
            "output/voice_*.mp3"
        ],
        "Test rows in Google Sheets": []
    }

    total_removed = 0
    total_size = 0

    for category, patterns in cleanup_items.items():
        if not patterns:
            continue

        print(f"\n🗑️  {category}:")
        category_count = 0

        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        print(f"   ✅ Deleted: {file_path} ({size / 1024 / 1024:.1f}MB)")
                        category_count += 1
                        total_size += size
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"   ✅ Deleted folder: {file_path}")
                        category_count += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to delete {file_path}: {e}")

        if category_count == 0:
            print(f"   Nothing to clean")

        total_removed += category_count

    # Clean up TEST rows from Google Sheets
    print(f"\n📊 Cleaning Google Sheets...")
    try:
        from dotenv import load_dotenv
        import gspread
        from google.oauth2.service_account import Credentials

        load_dotenv()

        creds_path = os.path.join(os.getcwd(), 'src/config/credentials.json')
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet('The17Project_Reels')

        # Find and delete TEST rows
        all_values = sheet.get_all_values()
        test_rows = []

        for i, row in enumerate(all_values):
            if len(row) >= 2 and row[1] == 'TEST':
                test_rows.append(i + 1)  # 1-indexed

        # Delete from bottom to top to maintain indices
        for row_num in reversed(test_rows):
            sheet.delete_rows(row_num)
            print(f"   ✅ Deleted TEST row {row_num}")

        if not test_rows:
            print(f"   No TEST rows to clean")

    except Exception as e:
        print(f"   ⚠️  Could not clean Google Sheets: {e}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"✅ CLEANUP COMPLETE!")
    print(f"{'=' * 70}")
    print(f"Files removed: {total_removed}")
    print(f"Space freed: {total_size / 1024 / 1024:.1f}MB")
    print(f"\nProject is now clean and ready for production!")

if __name__ == "__main__":
    cleanup_project()

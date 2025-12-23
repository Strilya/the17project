"""
Performance Comparison Script

Analyzes V1 vs V2 content performance from Google Sheets data.

Usage:
    python scripts/compare_performance.py

Prerequisites:
    - Google Sheets tracking spreadsheet with performance data
    - Columns: content_version, hook_style, views, likes, comments, followers_gained
"""

import os
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = os.getenv('SHEET_ID')
RANGE_NAME = 'Sheet1!A:Z'  # Adjust as needed


def load_sheet_data():
    """Load data from Google Sheets."""
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPES
        )

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])

        if not values:
            print('No data found in sheet.')
            return None

        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    except Exception as e:
        print(f"Error loading sheet data: {e}")
        return None


def analyze_performance(df):
    """Compare V1 vs V2 performance."""
    print("\n" + "="*70)
    print("📊 THE17PROJECT A/B TESTING RESULTS")
    print("="*70 + "\n")

    # Check for required columns
    required_columns = ['content_version', 'views', 'likes', 'comments', 'followers_gained']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print("⚠️  Missing required columns in Google Sheets:")
        for col in missing_columns:
            print(f"   - {col}")
        print("\n   Please add these columns to your tracking sheet:")
        print("   content_version, hook_style, views, likes, comments, followers_gained")
        return

    # Filter for videos with performance data
    df_tracked = df[df['views'].notna() & (df['views'] != '')]

    if len(df_tracked) == 0:
        print("⚠️  No performance data found in sheet.")
        print("   Make sure you've added views/likes/comments/followers columns")
        print("   and populated them after posting to Instagram.")
        return

    # Convert numeric columns
    numeric_cols = ['views', 'likes', 'comments', 'followers_gained']
    for col in numeric_cols:
        if col in df_tracked.columns:
            df_tracked[col] = pd.to_numeric(df_tracked[col], errors='coerce')

    # Split by version
    v1_data = df_tracked[df_tracked['content_version'] == 'v1']
    v2_data = df_tracked[df_tracked['content_version'] == 'v2']

    print(f"Videos analyzed:")
    print(f"  V1 (original): {len(v1_data)}")
    print(f"  V2 (improved): {len(v2_data)}")
    print()

    if len(v1_data) == 0 or len(v2_data) == 0:
        print("⚠️  Need both V1 and V2 videos with performance data to compare.")
        return

    # Calculate metrics
    metrics = {}

    for version, data in [('V1', v1_data), ('V2', v2_data)]:
        total_views = data['views'].sum()
        total_engagements = (data['likes'] + data['comments']).sum()

        metrics[version] = {
            'avg_views': data['views'].mean(),
            'avg_likes': data['likes'].mean(),
            'avg_comments': data['comments'].mean(),
            'avg_followers': data['followers_gained'].mean(),
            'engagement_rate': (total_engagements / total_views * 100) if total_views > 0 else 0,
            'follower_conversion': (data['followers_gained'].sum() / total_views * 100) if total_views > 0 else 0
        }

    # Print comparison
    print("PERFORMANCE COMPARISON:")
    print("-" * 70)
    print(f"{'Metric':<25} {'V1 (Original)':<20} {'V2 (Improved)':<20} {'Change'}")
    print("-" * 70)

    for metric, label in [
        ('avg_views', 'Avg Views'),
        ('avg_likes', 'Avg Likes'),
        ('avg_comments', 'Avg Comments'),
        ('avg_followers', 'Avg Followers Gained'),
        ('engagement_rate', 'Engagement Rate %'),
        ('follower_conversion', 'Follower Conversion %')
    ]:
        v1_val = metrics['V1'][metric]
        v2_val = metrics['V2'][metric]
        change = ((v2_val - v1_val) / v1_val * 100) if v1_val > 0 else 0

        change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        print(f"{label:<25} {v1_val:<20.2f} {v2_val:<20.2f} {change_symbol} {change:+.1f}%")

    print("-" * 70)
    print()

    # Decision recommendation
    print("RECOMMENDATION:")
    print("-" * 70)

    conversion_improvement = ((metrics['V2']['follower_conversion'] - metrics['V1']['follower_conversion'])
                             / metrics['V1']['follower_conversion'] * 100) if metrics['V1']['follower_conversion'] > 0 else 0

    if conversion_improvement > 50:
        print("✅ V2 shows significant improvement (>50% better conversion)")
        print("   RECOMMENDATION: Switch to V2 as default")
        print("   Action: Run 'cd /Users/ilyastr/Desktop/the17Project && git checkout master && git merge feature/improved-content-hooks'")
    elif conversion_improvement > 20:
        print("⚠️  V2 shows moderate improvement (20-50% better conversion)")
        print("   RECOMMENDATION: Continue testing for 1 more week")
        print("   Action: Generate 7 more of each version")
    elif conversion_improvement > 0:
        print("⚠️  V2 shows slight improvement (<20% better conversion)")
        print("   RECOMMENDATION: Test different hook styles")
        print("   Action: Focus on specific hook styles that performed best")
    else:
        print("❌ V2 is not performing better than V1")
        print("   RECOMMENDATION: Stick with V1 or revise V2 approach")
        print("   Action: Analyze which hook styles failed, revise prompts")

    print("-" * 70)
    print()

    # Hook style breakdown (if available)
    if 'hook_style' in df_tracked.columns and 'hook_style' in v2_data.columns:
        print("V2 HOOK STYLE PERFORMANCE:")
        print("-" * 70)

        v2_hook_performance = v2_data.groupby('hook_style').agg({
            'views': 'mean',
            'likes': 'mean',
            'followers_gained': 'mean'
        }).round(2)

        if len(v2_hook_performance) > 0:
            print(v2_hook_performance)
            print()
            best_hook = v2_hook_performance['followers_gained'].idxmax()
            print(f"Best performing hook style: {best_hook}")
            print("-" * 70)


if __name__ == "__main__":
    df = load_sheet_data()
    if df is not None:
        analyze_performance(df)
    else:
        print("Failed to load sheet data")

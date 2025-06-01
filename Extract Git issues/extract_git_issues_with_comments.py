import os
import requests
import time

# --- Configuration ---
repo = "explore/PrivateCloud"
states = ["open", "closed"]  # Or ["all"]
per_page = 100
sleep_seconds = 3

# Optional: use your GitHub token for higher rate limits
token = os.environ.get("GITHUB_TOKEN", "")  # Set in your environment
print(f"token: {token}")
headers = {"Authorization": f"Bearer {token}"} if token else {}

def fetch_issues_by_state(state):
    page = 1
    issues = []
    while True:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {"state": state, "per_page": per_page, "page": page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_issues = response.json()

        # Filter out pull requests
        filtered = [issue for issue in page_issues if "pull_request" not in issue]
        issues.extend(filtered)

        if len(page_issues) < per_page:
            break
        page += 1
    return issues

def save_issue_with_comments(issue):
    issue_number = issue["number"]
    issue_url = issue["url"]
    comments_url = issue.get("comments_url", "")

    issue_response = requests.get(issue_url, headers=headers)
    issue_response.raise_for_status()
    issue_data = issue_response.json()

    comments_response = requests.get(comments_url, headers=headers)
    comments_response.raise_for_status()
    comments = comments_response.json()

    filename = f"issue_{issue_number}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Issue #{issue_number}: {issue_data['title']}\n")
        f.write(f"State: {issue_data['state']}\n")
        f.write(f"Author: {issue_data['user']['login']}\n\n")
        f.write(f"Body:\n{issue_data.get('body', '')}\n\n")
        f.write("Comments:\n")
        for comment in comments:
            f.write(f"--- {comment['user']['login']} at {comment['created_at']} ---\n")
            f.write(f"{comment['body']}\n\n")

    print(f"Saved issue #{issue_number} to {filename}")
    time.sleep(sleep_seconds)

# --- Main Execution ---
all_issues = []
for state in states:
    print(f"Fetching issues with state: {state}")
    issues = fetch_issues_by_state(state)
    all_issues.extend(issues)
    print(f"Retrieved {len(issues)} '{state}' issues.")

print(f"\nTotal issues fetched: {len(all_issues)}")

for issue in all_issues:
    save_issue_with_comments(issue)
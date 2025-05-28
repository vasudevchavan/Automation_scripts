# Automation scripts to help increase productivity

## Extract_git_issues_with_comments
    This python script will help in fetching details of all open and closedissues in a text file.
    These text files can be used to train a LLM model.

### How to run it:
    Sample example:
        ```
        repo = "explore/PrivateCloud"
        url = f"https://api.github.com/repos/{repo}/issues"
        ```
    Replace these variable accoring to your requirement.
    Create ENV variable with below command:
        ```
        export GITHUB_TOKEN="aasfsdf11"
        ```
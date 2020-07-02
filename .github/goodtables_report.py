"""

Summarize the Frictionless Data JSON error output and if there are any errors, 
send a summary message to a given Slack channel. Send a more detailed 
error summary to std out and create a detailed txt file that can be accessed via GitHub
artifacts.

---

This script expects that you ran the following task:

    - name: Run goodtables
      run: goodtables validate datapackage.json --json -o error_summary.json

...which you can then follow with the following block that generates the 
goodtables report summary:

    - name: Summarize and send slack alert
      env:
        SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        ERROR_FILE: error_summary.json
        ERROR_MAX: 5
      if: ${{ always() }}
      run: python .github/goodtables_report.py

You'll need to define SLACK_WEBHOOK in your repo's secrets. `validate-csv.yml` 
can also be copied verbatim, assuming that the schema is named `datapackage.json`.

---

Links to...
- Generate a Slack token
    https://slack.com/apps/A0F7XDUAZ-incoming-webhooks
- API for POST requests / formatting text:
    https://api.slack.com/messaging

"""

import json
import requests
import os

ERROR_FILE = os.environ['ERROR_FILE']
REPO = os.environ['GITHUB_REPOSITORY']
ERROR_MAX = int(os.environ['ERROR_MAX'])

def main():
    with open(ERROR_FILE) as f: 
        error_json = json.load(f)

    # Create and print message to std out.
    stdout_string = f"Error Count: { error_json['error-count'] }\n"
    for table in error_json['tables']:
        if table['error-count']:
            stdout_string += f"\tTable: { table['resource-name'] }\n"
            stdout_string += f"\tError Count: { table['error-count'] }\n"
            for error in table['errors'][:ERROR_MAX]:
                stdout_string += f'\t\t{ error["message"] }\n'
            stdout_string += "\n"

    print(stdout_string)

    # Create a txt file that users can download as an artifact.
    with open('error_summary.txt', 'w') as f:
        f.write(stdout_string)

    # If there were no errors, end function and do not send a Slack message.
    if not error_json['error-count']:
        return

    # Create a slack payload.
    slack_message = (
        f"<https://github.com/{REPO}/actions/runs/{ os.environ['GITHUB_RUN_ID'] }|" +
        f"goodtables validation failed with { error_json['error-count'] } error(s)>"
    )

    j_payload = { 'text': slack_message }

    # post stringified payload to url
    requests.post(os.environ['SLACK_WEBHOOK'], json.dumps(j_payload))


if __name__ == '__main__':
    main()

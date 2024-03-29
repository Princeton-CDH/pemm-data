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
        SLACK_GOODTABLES_WEBHOOK: ${{ secrets.SLACK_GOODTABLES_WEBHOOK }}
        VALIDATION_OUTPUT_FILE: error_summary.json
        ERROR_MAX: 5
      if: ${{ always() }}
      run: python .github/goodtables_report.py

You'll need to define SLACK_GOODTABLES_WEBHOOK in your repo's secrets. `validate-csv.yml` 
can also be copied verbatim, assuming that the schema is named `datapackage.json`.

SLACK_GOODTABLES_WEBHOOK_2 is also an environment variable you can include if you'd
like to send the message to more than one Slack.

ERROR_MAX limits the number of errors listed on each CSVs output summary. If not defined,
no maximum will be used.

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

# Required vars
VALIDATION_OUTPUT_FILE = os.environ['VALIDATION_OUTPUT_FILE']
SCHEMA_PATH = os.environ['SCHEMA_PATH']
WEBHOOK = os.environ['SLACK_GOODTABLES_WEBHOOK']

# Optional vars
ERROR_MAX = None if 'ERROR_MAX' not in os.environ else int(os.environ['ERROR_MAX'])
WEBHOOK_2 = os.environ.get('SLACK_GOODTABLES_WEBHOOK_2')

# Github vars
REPO = os.environ['GITHUB_REPOSITORY']
RUN_ID = os.environ['GITHUB_RUN_ID']

def is_invalid_schema(error_json):
    """Send a Slack message and return true if the datapackage json is invalid."""

    try:
        with open(SCHEMA_PATH) as f:
            json.load(f)
    except Exception as err:
        j_payload = {
            'text': "There was an error loading the JSON:",
            'attachments': [
                {
                    "fallback": f'```{str(err)}```',
                    "color": "danger",
                    "fields":[{
                       "title": SCHEMA_PATH,
                       "value": f'```{str(err)}```'
                    }]
                }
            ]
        }

        # post stringified payload to url
        requests.post(WEBHOOK, json.dumps(j_payload))
        if WEBHOOK_2:
            requests.post(WEBHOOK_2, json.dumps(j_payload))

        return True
    
    return False


def main():
    # Load validation file
    with open(VALIDATION_OUTPUT_FILE) as f: 
        error_json = json.load(f)

    # Check if schema is valid
    # We assume that if the tables property is empty, goodtables didn't process
    #     the datapackage JSON
    if not error_json['tables']:
        if is_invalid_schema(error_json):
            return

    # Create and print message to std out.
    stdout_string = f"Error Count: { error_json['error-count'] }\n"
    for table in error_json['tables']:
        if table['error-count']:
            stdout_string += f"\tTable: { table['resource-name'] }\n"
            stdout_string += f"\tError Count: { table['error-count'] }\n"
            # When ERROR_MAX is None, python defaults to the entire array.
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
    plural = "" if error_json['error-count'] == 1 else "s"
    slack_message_prelude = (
        f"<https://github.com/{REPO}/actions/runs/{ RUN_ID }|" +
        f"goodtables validation failed with { error_json['error-count'] } error{plural}>"
    )
    
    # (This will be shown on mobile and notifications in lieu of attachments.)
    slack_message_fallback = f"Error Count: { error_json['error-count'] }\n"
    for table in error_json['tables']:
        if table['error-count']:
            slack_message_fallback += f"\tTable: { table['resource-name'] }\n"
            slack_message_fallback += f"\tError Count: { table['error-count'] }\n"
            slack_message_fallback += "\n"

    j_payload = {
        'text': slack_message_prelude,
        'attachments': [
            {
                "fallback": slack_message_fallback,
                "color": "danger",
                "fields":[{
                   "title": table['resource-name'] + '.csv',
                   "value": (
                        f"_Error count_: { table['error-count'] }\n" +
                        f"_Error type_: {', '.join(set([x['code'] for x in table['errors']]))}\n"
                    )
                }]
            } for table in error_json['tables'] if table['error-count'] != 0
        ]
    }

    # post stringified payload to url
    requests.post(WEBHOOK, json.dumps(j_payload))
    if WEBHOOK_2:
        requests.post(WEBHOOK_2, json.dumps(j_payload))


if __name__ == '__main__':
    main()

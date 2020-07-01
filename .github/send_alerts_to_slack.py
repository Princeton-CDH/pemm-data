"""

Summarize the Frictionless Data JSON error output and if there are any errors, 
send a summary message to a given Slack channel. Send a more detailed 
error summary to std out and create a detailed txt file that can be accessed via GitHub
artifacts.

To run elsewhere, define SLACK_WEBHOOK in your repo's secrets and change the 
top-level constants defined below. 

`validate-csv.yml` can also be copied verbatim, assuming that the schema is 
named `datapackage.json`.

Links to...
- Generate a Slack token
    https://slack.com/apps/A0F7XDUAZ-incoming-webhooks
- API for POST requests / formatting text:
    https://api.slack.com/messaging


"""

import json
import requests
import os

ERROR_FILE = 'error_summary.json'
REPO = 'Princeton-CDH/pemm-data'
CHANNEL = '#slack-webhook-test'
ERROR_MAX = 5

def main():
    with open(ERROR_FILE) as f: 
        j = json.load(f)

    # Create and print message to std out.
    stdout_string = f"Error Count: { j['error-count'] }\n"
    for table in j['tables']:
        if table['error-count'] != 0:
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
    if j['error-count'] == 0:
        return

    # Create a slack payload.
    slack_message_prelude = (
        f"🚨 Goodtables found {j['error-count']} error(s) in the latest sync." +
        f" For more details, head to <https://github.com/{REPO}" +
        f"/actions/runs/{os.environ['GITHUB_RUN_ID']}" + 
        "?check_suite_focus=true|GitHub Actions>"
    )
    
    # (This will be shown on mobile and notifications in lieu of attachments.)
    slack_message_fallback = f"Error Count: { j['error-count'] }\n"
    for table in j['tables']:
        if table['error-count'] != 0:
            slack_message_fallback += f"\tTable: { table['resource-name'] }\n"
            slack_message_fallback += f"\tError Count: { table['error-count'] }\n"
            slack_message_fallback += "\n"

    j_payload = {
        'channel': CHANNEL,
        'text': slack_message_prelude,
        'attachments': [
            {
                "fallback": slack_message_fallback,
                "color": "danger",
                "fields":[{
                   "title": table['resource-name'] + '.csv',
                   "value": (
                        f"_Error Count_: { table['error-count'] }\n" +
                        f"_Error type(s)_: {', '.join(set([x['code'] for x in table['errors']]))}\n"
                    )
                }]
            } for table in j['tables'] if table['error-count'] != 0
        ]
    }

    # post stringified payload to url
    requests.post(os.environ['SLACK_WEBHOOK'], json.dumps(j_payload))


if __name__ == '__main__':
    main()

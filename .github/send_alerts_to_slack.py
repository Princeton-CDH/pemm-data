"""
send_alerts_to_slack.py

Summarize the Frictionless Data JSON error output and if there are any errors, 
send a summary message to Slack. Also send a more detailed error summary to STDOUT

"""

import json
import os

def main():
    with open('error_summary.json') as f: 
        j = json.load(f)

    # create std out message
    giant_string = ""

    giant_string += f"Error Count: {j['error-count']}\n"
    for table in j['tables']:
        if table['error-count'] != 0:
            giant_string += f"\tTable: {table['resource-name']}\n"
            giant_string += f"\tError Count: {table['error-count']}\n"
            for error in table['errors'][:5]:
                giant_string += f'\t\t{error["message"]}\n'
            giant_string += "\n"

    print(giant_string)

    # create slack message
    if j['error-count'] != 0:
        slack_message = ""
        slack_message += f"Error Count: {j['error-count']}\n"
        for table in j['tables']:
            if table['error-count'] != 0:
                slack_message += f"\tTable: {table['resource-name']}\n"
                slack_message += f"\tError Count: {table['error-count']}\n"
                slack_message += "\n"

        slack_message = (
            "It looks like there were a few errors in the latest data build." +
            "Here's a summary\n\n" + 
                slack_message +
            "For more details, head to <https://github.com/Princeton-CDH/" +
            f"pemm-data/actions/runs/{os.environ['GITHUB_RUN_ID']}" + 
            "?check_suite_focus=true|GitHub Actions>"
        )
        
        j_payload = {
            'channel': '#slack-webhook-test',
            'username': 'webhookbot',
            'text': slack_message
        }

        s_payload = json.dumps(j_payload)
        s_payload = s_payload.replace('"', '\\"')

        escaped_payload = 'payload="' + s_payload + '"'

        command = 'curl -X POST --data-urlencode '
        command += f'{escaped_payload} '
        command += os.environ['SLACK_WEBHOOK']

        os.system(command)

if __name__ == '__main__':
    main()
import sys
import os
from copy import deepcopy
import requests
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

SCAN_API_URL = "api/v1/cloud-scan-rules?project=Central+Console"


def _get_update_account_info():
    try:
        get_user_input = int(sys.argv[2])

    except IndexError:
        sys.exit(
            "Error: Please enter a comma separated list of account numbers, or the number of accounts you want to modify. Use 0 if you'd like to update all accounts"
        )

    if isinstance(get_user_input, int) and len(str(get_user_input)) != 12:
        update_account_numbers = None
        update_account_count = get_user_input

    else:
        update_account_numbers = str(get_user_input).split(",")
        update_account_count = len(update_account_numbers)


    return update_account_numbers, update_account_count


def _get_base_url():
    try:
        base_url = sys.argv[1]

    except IndexError:
        sys.exit("Error: Please provide your Console path")

    return base_url


def _get_new_custom_tags():
    try:
        custom_tags = sys.argv[3].split(",")

    except IndexError:
        sys.exit("Error: Please provide custom tags.")

    return custom_tags


def _get_token():
    try:
        cwp_token = os.environ["CWP_TOKEN"]

    except KeyError:
        sys.exit('Error: Please set the "CWP_TOKEN" environment variable')

    return cwp_token


def _get_response_error(response):
    error_response = response.get("err").capitalize()
    sys.exit(f"Error: {error_response}")


def get_cwp_configs(headers, customer_url, account_count=50):
    get_config_url = f"{customer_url}&offset=0&limit={account_count}"

    response_object = requests.get(
        get_config_url,
        headers=headers,
        verify=False,
    )

    response = response_object.json()
    if response_object.status_code != 200:
        _get_response_error(response)

    return response


def add_agentless_custom_tags(headers, base_url, new_cwp_config_payload):

    response_object = requests.put(
        base_url,
        headers=headers,
        json=new_cwp_config_payload,
        verify=False,
    )

    response = response_object
    if response_object.status_code != 200:
        _get_response_error(response.json())

    print(f"Applied agentless tags to {len(new_cwp_config_payload)} accounts")

    return response


def _build_new_cwp_config_payload(new_cwp_configs, new_custom_tags, update_account_numbers, update_account_count
):
    new_cwp_config_payload = []

    for new_cwp_config in new_cwp_configs:
        if not new_cwp_config["agentlessScanSpec"]["enabled"]:
            continue

        if update_account_numbers and new_cwp_config["credential"]["accountID"] not in update_account_numbers:
            print(new_cwp_config["credential"]["accountID"])
            continue

        if new_cwp_config["agentlessScanSpec"].get("customTags"):
            new_cwp_config["agentlessScanSpec"]["customTags"] = list(
                set(new_custom_tags + new_cwp_config["agentlessScanSpec"]["customTags"])
            )

        else:
            new_cwp_config["agentlessScanSpec"]["customTags"] = new_custom_tags

        new_cwp_config_payload.append(new_cwp_config)

        if update_account_count == 0:
            continue

        elif len(new_cwp_config_payload) == update_account_count:
            break

    return new_cwp_config_payload


def _print_report(new_cwp_config_payload):
    print("Updated the following accounts:")

    for account in new_cwp_config_payload:
        details = account["credential"]
        print(
            f"Cloud: {details['type']}, Account ID: {details['accountID']}, Account Name: {details['accountName']}"
        )


def main():
    update_account_numbers, update_account_count = _get_update_account_info()
    base_url = _get_base_url()
    customer_url = f"{base_url}/{SCAN_API_URL}"
    token = _get_token()
    new_custom_tags = _get_new_custom_tags()

    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    original_cwp_configs = get_cwp_configs(headers, customer_url)
    new_cwp_configs = deepcopy(original_cwp_configs)
    new_cwp_config_payload = _build_new_cwp_config_payload(
        new_cwp_configs, new_custom_tags, update_account_numbers, update_account_count
    )

    add_agentless_custom_tags(headers, customer_url, new_cwp_config_payload)
    _print_report(new_cwp_config_payload)


if __name__ == "__main__":
    main()

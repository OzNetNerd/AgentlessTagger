# Agentless Tagger

At present, the UI limits agentless scanner instance custom tags to 10. However, this limit is not enforced when the tags are applied through the API.

The script iterates over customers' accounts and identifies the ones which have agentless scanning enabled. It then applies the specified custom tags to them. If accounts have existing tags applied, the script appends the new ones and leaves the original ones intact.  

# Usage Instructions

1. Navigate to "Compute" --> "System"
2. Click "Utilities". Take note of the "Path to Console" and URL and the "API token".
3. Set the `CWP_TOKEN` environment variable to the "API token" found in the previous step.
4. Run the script using the following syntax:

```
python3 agentless_tagger.py <PATH_TO_CONSOLE_URL> <NUMBER_OF_ACCOUNTS> <KEY_VALUE_PAIRS>
```

Example:

```
python3 agentless_tagger.py https://us-east1.cloud.twistlock.com/us-1-111111111 0 name1:key1,name2:key2,name3:key3
```

**Note:** `<NUMBER_OF_ACCOUNTS>` is used to control how many accounts the script updates. It can be used for testing purposes and implementing the change in batches. Setting it to `0` will ensure all accounts get updated.


# Known issues

Pagination has not been implemented yet. Therefore, only a maximum of 50 accounts will be updated at this point in time.
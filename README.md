# tabbyAPItesting
Basic code and tests of tabbyAPI, including json structured generation

The code assumes you have a tabbyAPI server running on 127.0.0.1:5000 with a chat model already loaded

call_tabby_basic.py : A very basic no-frills call to the API with a simple prompt

call_tabby_json_validate.py : A call using a simple 2-element json schema that tracks how often the returned response conforms

The schema is asking for a json that looks like {"country": "COUNTRY_NAME","capital":"CAPITAL_NAME"}

The schema is followed approximately 75% of the time.
The 25% failures are approximately 15% no country present (only the capital), 10% no closing "}".  About 1% of the time it returns {} (i.e.,empty json brackets)

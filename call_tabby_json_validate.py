import requests
import yaml
import json
import pydantic
from json_to_pydantic import *
import jsonschema

def validate_json(json_string, json_schema):
    try:
        # Parse the JSON string
        data = json.loads(json_string)
        
        schema = json.loads(json_schema)

        # Validate against the schema
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as validation_err:
        print(f"Validation Error: {validation_err}")
        return False
    except json.JSONDecodeError as json_err:
        print(f"JSON Parsing Error: {json_err}")
        return False



def read_text_file(filename):
    """
    Reads a text file and returns its content as a string.

    :param filename: The name of the text file to read.
    :return: The content of the file as a string.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_yaml_key_value(filename, key):
    """
    Reads a YAML file and returns the value of a specific key.

    :param filename: The name of the YAML file to read.
    :param key: The key whose value needs to be retrieved.
    :return: The value of the key as a string, or an error message if the key is not found.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Find the key in the YAML structure
        value = data.get(key)
        if value is None:
            print(f"Error: The key '{key}' was not found in the file.")
            return None
        return str(value)
    
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse the YAML file. Details: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def call_openai_compatible_api(messages, url="http://127.0.0.1:5000/v1/chat/completions", model="gpt-4",
                                max_tokens=1000, temperature=1.0, top_p=1.0, n=1,
                                stream=False, stop=None, presence_penalty=0.0,
                                frequency_penalty=0.0, logit_bias=None, user=None, json_schema_str = None, API_key = None):
    """
    Calls an OpenAI-compatible v1/completions endpoint with all available settings.

    Args:
        messages (list): List of message dictionaries in the format:
                         [{"role": "system", "content": "your system message"},
                          {"role": "user", "content": "your user input"}].
        url (str): API endpoint URL (default: "http://127.0.0.1:5000/v1/completions").
        model (str): The model to use (default: "gpt-4").
        max_tokens (int): Maximum tokens to generate (default: 1000).
        temperature (float): Sampling temperature (default: 1.0).
        top_p (float): Nucleus sampling probability (default: 1.0).
        n (int): Number of responses to generate (default: 1).
        stream (bool): Whether to stream responses (default: False).
        stop (str or list): Stop sequences for output generation (default: None).
        presence_penalty (float): Penalize new tokens based on their presence (default: 0.0).
        frequency_penalty (float): Penalize new tokens based on frequency (default: 0.0).
        logit_bias (dict): Adjust the likelihood of specific tokens (default: None).
        user (str): User identifier for tracking purposes (default: None).

    Returns:
        dict: The API response.
    """

    auth_string = f"Bearer {API_key}"
    headers = {
        "x-admin-key": API_key,
        "x-api-key": API_key,
        "authorization": auth_string
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stream": stream,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "stop": ["<|im_end|>"],
        "user": user
    }

    # Direct conversion from JSON schema string
    if (json_schema_str):
        pydantic_model = json_schema_to_pydantic(json_schema_str)
        payload["json_schema"] = pydantic_model.schema()

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Define the message history
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
#        {"role": "system", "content": 'You are a helpful assistant.  Your response should be in json format.  The response should contain two keys, "country" and "capital".  The json should be in the format of {"country":"COUNTRY_NAME", "capital","CAPITAL_NAME"}'},
        {"role": "user", "content": "What is the capital of France?"}
    ]

    json_schema_str = None
    json_schema_str = read_text_file("capital_json_schema.txt")

    API_key = None
    keyfile = "/home/andrew/tabbyAPI/api_tokens.yml"
    API_key = get_yaml_key_value(keyfile,"admin_key") # Either will work
    API_key = get_yaml_key_value(keyfile,"api_key")


    fails = 0
    wins = 0

    max_fails = 20
    max_wins = 100

    while (fails < max_fails and wins < max_wins):

        # Call the API
        response = call_openai_compatible_api(
            messages=messages,
            url="http://127.0.0.1:5000/v1/chat/completions",
            max_tokens=100,
            temperature=0.7,
            top_p=1.0,
            n=1,
            stream=False,
            stop=None,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            logit_bias=None,
            json_schema_str = json_schema_str,
            API_key = API_key,
            user="test_user"
        )

        ai_response = response["choices"][0]["message"]["content"]


        if (json_schema_str):
            is_right = validate_json(ai_response, json_schema_str)
        else:
            is_right = True

        if (is_right):
            wins += 1
        else:
            fails += 1
            if response and "choices" in response:
                print("AI: " + response["choices"][0]["message"]["content"])
            else:
                print("Generation error")

    # Print the last response
    for message in messages:
        print(message["role"] + ": " + message["content"])
    if response and "choices" in response:
        print("AI: " + response["choices"][0]["message"]["content"])

    print("Worked: "+str(wins))
    print("Failed: "+str(fails))

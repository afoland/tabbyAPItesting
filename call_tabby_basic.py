import requests
import yaml
import json

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

def call_openai_compatible_api(messages, url="http://127.0.0.1:5000/v1/chat/completions", 
                                max_tokens=1000, temperature=1.0, top_p=1.0, n=1,
                                stream=False, stop=None, presence_penalty=0.0,
                                frequency_penalty=0.0, logit_bias=None, user=None, API_key = None):
    """
    Calls an OpenAI-compatible v1/chat/completions endpoint with available settings.

    Additional settings may be available, check your API documents

    Args:
        messages (list): List of message dictionaries in the format:
                         [{"role": "system", "content": "your system message"},
                          {"role": "user", "content": "your user input"}].
        url (str): API endpoint URL (default: "http://127.0.0.1:5000/v1/chat/completions").
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
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stream": stream,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "user": user
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":

    keyfile = YOUR_API_KEYS_YML_KEYFILE_LOCATION_HERE
    API_key = None
    if (keyfile):
        API_key = get_yaml_key_value(keyfile,"admin_key")
        API_key = get_yaml_key_value(keyfile,"api_key")
        # Either will work for completions.  For some calls, e.g., model-setting,
        # you may need to use admin_key
    else:
        print("You probably need to provide a .yml keyfile with api keys")
        # The code will continue to try anyway, in case you have turned 
        # authorization off at the server

    # Define the message history
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]

    # Example call of the API
    response = call_openai_compatible_api(
        messages=messages,
        url="http://127.0.0.1:5000/v1/chat/completions",
        max_tokens=50,
        temperature=0.7,
        top_p=1.0,
        n=1,
        stream=False,
        stop=None,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        logit_bias=None,
        API_key = API_key,
        user="test_user"
    )

    # Print the response
    for message in messages:
        print(message["role"] + ": " + message["content"])
    if response and "choices" in response:
        for idx in range(len(response["choices"])):
            if (len(response["choices"]) > 1):
                print(f"AI (Response {idx}): " + response["choices"][idx]["message"]["content"])
            else: # Just make it a little neater for the usual case
                print(f"AI: " + response["choices"][idx]["message"]["content"])

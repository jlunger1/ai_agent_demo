import requests

def test_agent():
    # URL of your backend's `/process-query` endpoint
    url = "http://127.0.0.1:8000/process-query"

    # Example query to send to the agent
    test_query = "Find me a flight from Boston to Los Angeles on February 1st."

    # POST request payload
    payload = {"query": test_query}

    try:
        # Make the POST request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            print("Agent Response:")
            print(response.json()["response"])  # Print the response from the agent
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_agent()

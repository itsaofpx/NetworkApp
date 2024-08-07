import json

# Define response codes and protocol codes
RESPONSE_CODES = {
    "200": "OK",
    "201": "Created",
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "500": "Internal Server Error"
}

def create_message(command, *args):
    """
    Create a message to send from the client to the server.
    """
    message = {"command": command}
    if args:
        message["args"] = list(args)
    return json.dumps(message)

def parse_message(message):
    """
    Parse a received message from the server or client.
    """
    try:
        data = json.loads(message)
        command = data.get("command")
        args = data.get("args", [])
        return command, args
    except json.JSONDecodeError:
        return None, []

def create_response(status_code, message, protocol_code=""):
    """
    Create a response message with a specific response code and optional protocol code.
    """
    response_code_message = RESPONSE_CODES.get(str(status_code), "Unknown")
    return f"{status_code} {response_code_message}\n{protocol_code} {message}"

def parse_response(response):
    """
    Parse a response received from the server.
    """
    try:
        parts = response.split("\n", 1)
        status_code_message = parts[0].split(maxsplit=1)
        status_code = int(status_code_message[0])
        message = status_code_message[1] if len(status_code_message) > 1 else ""
        protocol_code = parts[1] if len(parts) > 1 else ""
        return status_code, message.strip(), protocol_code.strip()
    except Exception as e:
        print(f"Error parsing response: {e}")
        return 500, "Internal server error", ""

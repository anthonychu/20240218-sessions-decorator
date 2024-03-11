import sys
import uuid
from azure.identity import DefaultAzureCredential
import requests
import functools
import inspect
import textwrap


class CodeInterpreterSessionPool():

    def __init__(self, subscription_id, resource_group, sessions_api_base_url, session_pool, session_id=None):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.sessions_api_base_url = sessions_api_base_url
        self.session_pool = session_pool

    def session(self, session_id=None):
        return Session(self.subscription_id, self.resource_group, self.sessions_api_base_url, self.session_pool, session_id=None)


class Session():

    def __init__(self, subscription_id, resource_group, sessions_api_base_url, session_pool, session_id=None):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.sessions_api_base_url = sessions_api_base_url
        self.session_pool = session_pool
        self.session_id = str(uuid.uuid4()) if session_id is None else session_id
    

    def _strip_decorators(self, func_source):
        func_source = textwrap.dedent(func_source)
        lines = func_source.split("\n")
        # remove every line until the function definition
        while lines and not lines[0].startswith("def "):
            lines.pop(0)

        return "\n".join(lines)


    def _convert_to_arg(self, variable):
        # doesn't support all types
        if isinstance(variable, str):
            # this fails if string has newlines
            escaped = variable.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return str(variable)


    def remote(self, func=None):
        def decorator_remote(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                
                credential = DefaultAzureCredential()
                access_token = credential.get_token("https://acasessions.io/.default").token

                api_url = f"{self.sessions_api_base_url}subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/sessionPools/{self.session_pool}/python/execute"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }

                func_source = self._strip_decorators(inspect.getsource(func))
                func_name = func.__name__

                command = f"{func_source}\n\n{func_name}({', '.join([self._convert_to_arg(arg) for arg in args])})"
                body = {
                    "properties": {
                        "identifier": self.session_id,
                        "codeInputType": "inline",
                        "executionType": "synchronous",
                        "pythonCode": command,
                    }
                }

                print(f"Executing function in session ID: {self.session_id}")
                response = requests.post(api_url, headers=headers, json=body)
                response.raise_for_status()
                response_json = response.json()
                result = response_json
                
                print(result['stderr'], file=sys.stderr) if result['stderr'] else None
                print(result['stdout']) if result['stdout'] else None

                print(f"Finished executing function. Status: {result['status']} ({result['executionTimeInMilliseconds']}ms)")
                
                if result['status'] != 'Success':
                    raise Exception(f"Error: {result['status']} - {result['stderr']}")

                return result['result']
            return wrapper
        
        if func:
            return decorator_remote(func)
        return decorator_remote

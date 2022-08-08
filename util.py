import json
import time
from functools import wraps
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

"""
TODO: Write whatever class or function you may need
but, don't use any third party library
feel free to make any changes in the given class and its methods' arguments or implementation as you see fit
"""


class NetworkRequest:
    @staticmethod
    def _request(req):
        result = {}
        try:
            with urlopen(req) as res:
                body = res.read().decode("utf-8")
                result["body"] = json.loads(body)
                result["code"] = res.status
        except HTTPError as error:
            result["code"] = error.status
            print(error.status, error.reason)
        except URLError as error:
            print(error.reason)
        except TimeoutError:
            print("Request timed out")
        return result

    @staticmethod
    def get(url, data={}, headers={}):
        req = Request(url=url, data=json.dumps(data).encode("utf-8"), headers=headers, method="GET")
        req.add_header("Content-type", "application/json")
        return NetworkRequest._request(req)

    @staticmethod
    def post(url, data={}, headers={}):
        req = Request(url=url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        req.add_header("Content-type", "application/json")
        return NetworkRequest._request(req)

    @staticmethod
    def put(url, data={}, headers={}):
        req = Request(url=url, data=json.dumps(data).encode("utf-8"), headers=headers, method="PUT")
        req.add_header("Content-type", "application/json")
        return NetworkRequest._request(req)

    @staticmethod
    def delete(url, data={}, headers={}):
        req = Request(url=url, data=json.dumps(data).encode("utf-8"), headers=headers, method="DELETE")
        req.add_header("Content-type", "application/json")
        return NetworkRequest._request(req)


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"(time taken: {elapsed_time} seconds)")
        return result

    return timeit_wrapper


class TweeterRequest:
    API_URL = "https://intern-test-server.herokuapp.com/api"

    def __init__(self, username, password) -> None:
        tokens = NetworkRequest.post(f"{type(self).API_URL}/auth", {"username": username, "password": password})["body"]
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

    def refresh_token_on_failure(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if result["code"] == 401:
                print("refreshing token")
                new_tokens = NetworkRequest.post(
                    f"{type(self).API_URL}/auth/token", {"refresh_token": self.refresh_token}
                )["body"]
                self.access_token, self.refresh_token = new_tokens["access_token"], new_tokens["refresh_token"]
                result = func(self, *args, **kwargs)
            return result["body"]

        return wrapper

    @timeit
    @refresh_token_on_failure
    def get_recent_tweets(self):
        return NetworkRequest.get(
            f"{type(self).API_URL}/tweets", headers={"Authorization": f"Bearer {self.access_token}"}
        )

    @timeit
    @refresh_token_on_failure
    def post_tweet(self, tweet):
        return NetworkRequest.post(
            f"{type(self).API_URL}/tweets",
            data={"text": tweet},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

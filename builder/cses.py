import requests

from .fetcher import Fetcher
from bs4 import BeautifulSoup
from typing import List, Tuple

class _CsesUrl:
    PREFIX = "https://cses.fi/"

    @staticmethod
    def problem_list() -> str:
        return _CsesUrl.PREFIX + "problemset/"

    @staticmethod
    def problem_stats(problem_id: int) -> str:
        return _CsesUrl.PREFIX + f"problemset/stats/{problem_id}/"

    @staticmethod
    def login_page() -> str:
        return  _CsesUrl.PREFIX + "login/"

class CsesProblem:
    def __init__(self, problem_id: int, title: str, solves: int, attempts: int):
        self.problem_id = problem_id
        self.title = title
        self.solves = solves
        self.attempts = attempts

    def __repr__(self):
        return f"CsesProblem(problem_id={self.problem_id}, title='{self.title}', solves={self.solves}, attempts={self.attempts})"

class Cses:
    def __init__(self, username: str, password: str):
        self.fetcher = Fetcher()

        resp = self.fetcher.session.get(_CsesUrl.login_page())
        soup = BeautifulSoup(resp.text, "html.parser")
        token = soup.find("input", {"name": "csrf_token"})["value"]

        payload = {
            "nick": username,
            "pass": password,
            "csrf_token": token
        }

        resp = self.fetcher.session.post(_CsesUrl.login_page(), data=payload)

        if "logout" not in resp.text:
            raise ValueError("Login failed. Please check your username and password.")


    def get_problem_stats(self, problem_id: int) -> Tuple[List[Tuple[int, float]], List[Tuple[int, int]]]:
        """
        Fetches the statistics of a specific problem.
        It returns two lists:
        - top 5 in runtime: A list of tuples (user_id, time (in seconds))
        - top 5 in code size: A list of tuples (user_id, code_size (in characters))

        :param problem_id:
        :return:
        """
        content = self.fetcher.fetch(_CsesUrl.problem_stats(problem_id), cache_timeout = 60 * 60 * 24 * 3) # cache for 3 days

        soup = BeautifulSoup(content, "html.parser")

        tables = soup.find_all("table", class_="narrow")

        best_times = []
        best_code_sizes = []

        for table in tables:
            for tr in table.find_all("tr"):
                a = tr.find_all("a")[0]
                user_id = int(a["href"].split("/")[-1])
                for td in tr.find_all("td"):
                    if td.find("a") is not None:
                        continue

                    if td.text.endswith("ch."):
                        code_size = int(td.text.replace("ch.", "").strip())
                        best_code_sizes.append((user_id, code_size))
                    if td.text.endswith("s"):
                        time = float(td.text.replace("s", "").strip())
                        best_times.append((user_id, time))

        return best_times, best_code_sizes


    def get_problems(self) -> list[CsesProblem]:
        """
        Lists all cses problems
        """
        content = self.fetcher.fetch(_CsesUrl.problem_list())

        soup = BeautifulSoup(content, "html.parser")

        problem_lists = soup.find_all("ul", class_="task-list")
        problems = []
        for ul in problem_lists:
            for li in ul.find_all("li", class_="task"):
                link = li.find("a")
                name = link.text.strip()
                problem_id = link["href"].split("/")[-1]
                detail = li.find("span", class_="detail").text.strip()
                solves, attempts = [int(x.strip()) for x in detail.split("/")]
                problems.append(CsesProblem(int(problem_id), name, solves, attempts))

        return problems

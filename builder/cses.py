from .fetcher import Fetcher
from bs4 import BeautifulSoup
from typing import List, Tuple

# A Collection of URLs used in CSES
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

    @staticmethod
    def leaderboard(page: int) -> str:
        return _CsesUrl.PREFIX + f"problemset/stats/p/{page}/"

    @staticmethod
    def user_page(user_id: int) -> str:
        return _CsesUrl.PREFIX + f"problemset/user/{user_id}/"

# Represents a CSES problem with its details
# It does not have any special functionality
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
        """
        Initializes the Cses instance by logging in with the provided username and password.

        :param username:
        :param password:
        :raises ValueError: If login fails due to incorrect credentials.
        """
        self.fetcher = Fetcher()
        self.user_id_to_username = {}

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

        # Find tables and extract data
        for table in tables:
            for tr in table.find_all("tr"):
                a = tr.find_all("a")[0]
                user_id = int(a["href"].split("/")[-1])
                user_name = a.text
                self.user_id_to_username[user_id] = user_name
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
        # Extract data from the problem list
        for ul in problem_lists:
            for li in ul.find_all("li", class_="task"):
                link = li.find("a")
                name = link.text.strip()
                problem_id = link["href"].split("/")[-1]
                detail = li.find("span", class_="detail").text.strip()
                solves, attempts = [int(x.strip()) for x in detail.split("/")]
                problems.append(CsesProblem(int(problem_id), name, solves, attempts))

        return problems

    def get_username(self, user_id: int) -> str:
        """
        Fetches the username for a given user ID.

        :param user_id:
        :return: username
        :raises ValueError: If the username for the given user ID is not found.
        """
        if user_id in self.user_id_to_username:
            return self.user_id_to_username[user_id]

        content = self.fetcher.fetch(_CsesUrl.user_page(user_id), cache_timeout = 60 * 60 * 24) # valid for 24 hours

        soup = BeautifulSoup(content, "html.parser")

        for h2 in soup.find_all("h2"):
            if h2.text.startswith("Statistics for"):
                username = h2.text.replace("Statistics for", "").strip()
                self.user_id_to_username[user_id] = username
                return username

        raise ValueError(f"Username for user_id {user_id} not found.")

    def get_leaderboard(self, num_pages: int) -> List[int]:
        """
        Fetches the leaderboard user IDs from the first num_pages pages.

        :param num_pages:
        :return: list of user IDs
        """

        ret = []

        for page in range(num_pages):
            content = self.fetcher.fetch(_CsesUrl.leaderboard(page + 1), cache_timeout = 60 * 60 * 6) # valid for 6 hours
            soup = BeautifulSoup(content, "html.parser")

            for table in soup.find_all("table"):
                if "summary-table" in table["class"]:
                    continue
                for tr in table.find_all("tr"):
                    a = tr.find("a")
                    if a is None:
                        continue
                    user_id = int(a["href"].split("/")[-2])
                    user_name = a.text
                    self.user_id_to_username[user_id] = user_name
                    ret.append(user_id)

        assert len(ret) == len(set(ret))
        return ret

    def get_solved_unsolved(self, user_id: int) -> Tuple[List[int], List[int]]:
        """
        Fetches the list of solved and unsolved problem IDs for a given user in separate lists.

        :param user_id:
        :return: list of solved and list of unsolved problem IDs
        """
        content = self.fetcher.fetch(_CsesUrl.user_page(user_id), cache_timeout = 60 * 60 * 24) # valid for 24 hours
        soup = BeautifulSoup(content, "html.parser")

        solved = []
        unsolved = []

        for td in soup.find_all("td"):
            for a in td.find_all("a"):
                problem_id = int(a["href"].split("/")[-2])
                if "full" not in a["class"]:
                    unsolved.append(problem_id)
                else:
                    solved.append(problem_id)


        return solved, unsolved

from fetcher import Fetcher
from bs4 import BeautifulSoup

class _CsesUrl:
    PREFIX = "https://cses.fi/problemset/"

    @staticmethod
    def problem_list() -> str:
        return _CsesUrl.PREFIX

    @staticmethod
    def problem_stats(problem_id: int) -> str:
        return _CsesUrl.PREFIX + f"stats/{problem_id}/"

class CsesProblem:
    def __init__(self, problem_id: int, title: str):
        self.problem_id = problem_id
        self.title = title

    def __repr__(self):
        return f"CsesProblem(id={self.problem_id}, title='{self.title}')"

class Cses:
    def __init__(self):
        self.fetcher = Fetcher()

    def list_problems(self) -> list[CsesProblem]:
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
                problems.append(CsesProblem(int(problem_id), name))

        return problems

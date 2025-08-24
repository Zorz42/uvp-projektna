from .fetcher import Fetcher
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
    def __init__(self, id: int, title: str, solves: int, attempts: int):
        self.id = id
        self.title = title
        self.solves = solves
        self.attempts = attempts

    def __repr__(self):
        return f"CsesProblem(id={self.id}, title='{self.title}', solves={self.solves}, attempts={self.attempts})"

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
                detail = li.find("span", class_="detail").text.strip()
                solves, attempts = [int(x.strip()) for x in detail.split("/")]
                problems.append(CsesProblem(int(problem_id), name, solves, attempts))

        return problems

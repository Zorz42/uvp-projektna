from .cses import Cses
import pandas as pd
import os

def build():
    username = os.getenv("CSES_USERNAME")
    password = os.getenv("CSES_PASSWORD")

    cses_instance = Cses(username, password)
    problems = cses_instance.get_problems()

    os.makedirs("data", exist_ok=True)

    data = [(i.problem_id, i.title, i.solves, i.attempts, i.solves / i.attempts) for i in problems]
    df = pd.DataFrame(data, columns=["id", "title", "solves", "attempts", "solve_ratio"])

    df.to_csv("data/cses_problems.csv", index=False, encoding="utf-8")

    for problem in problems:
        cses_instance.get_problem_stats(problem.problem_id)

    print("Total requests made:", cses_instance.fetcher.get_num_requests())





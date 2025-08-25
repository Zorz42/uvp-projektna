from .cses import Cses, CsesProblem
import pandas as pd
import os

def problem_score(problem: CsesProblem) -> float:
    """
    Score a problem based on difficulty and popularity.
    Higher score = harder or more “exclusive” problem.
    """
    # Solve ratio (0 < ratio <= 1)
    solve_ratio = problem.solves / problem.attempts if problem.attempts > 0 else 0

    # Base score: inverse of solve ratio
    ratio_score = 1 - solve_ratio

    # Add a small weight for total solves
    solves_score = 1 / (problem.solves + 1)

    return 70 * ratio_score + 30 * solves_score

def build():
    username = os.getenv("CSES_USERNAME")
    password = os.getenv("CSES_PASSWORD")

    cses_instance = Cses(username, password)
    problems = cses_instance.get_problems()

    os.makedirs("data", exist_ok=True)

    data = [(i.problem_id, i.title, i.solves, i.attempts, i.solves / i.attempts, problem_score(i)) for i in problems]
    df = pd.DataFrame(data, columns=["id", "title", "solves", "attempts", "solve_ratio", "score"])

    df.to_csv("data/cses_problems.csv", index=False, encoding="utf-8")

    users = {}

    for problem in problems:
        stats = cses_instance.get_problem_stats(problem.problem_id)
        for user_id, _ in stats[0] + stats[1]:
            if user_id not in users:
                users[user_id] = 0
            users[user_id] += 1

    user_data = [(user_id, cses_instance.get_username(user_id), count) for user_id, count in users.items()]
    user_df = pd.DataFrame(user_data, columns=["user_id", "username", "appearances"])

    user_df = user_df.sort_values(by="appearances", ascending=False)

    user_df.to_csv("data/cses_users.csv", index=False, encoding="utf-8")

    print("Total requests made:", cses_instance.fetcher.get_num_requests())





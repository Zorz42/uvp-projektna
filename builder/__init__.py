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

    users = {}

    for problem in problems:
        stats = cses_instance.get_problem_stats(problem.problem_id)
        for user_id, _ in stats[0] + stats[1]:
            if user_id not in users:
                users[user_id] = 0
            users[user_id] += 1

            if cses_instance.get_username(user_id) == 'jakob@zorz.si':
                print("Problem ", problem.title)

    user_data = [(user_id, cses_instance.get_username(user_id), count) for user_id, count in users.items()]
    user_df = pd.DataFrame(user_data, columns=["user_id", "username", "appearances"])

    user_df = user_df.sort_values(by="appearances", ascending=False)

    user_df.to_csv("data/cses_users.csv", index=False, encoding="utf-8")

    print("Total requests made:", cses_instance.fetcher.get_num_requests())





from .cses import Cses, CsesProblem
import pandas as pd
import os
import math

def score_problem(problem: CsesProblem, ld_score: float) -> float:
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

    return math.log(70 * ratio_score + 30 * solves_score + 100 * math.sqrt(ld_score) + 3) * 10

def score_user(problem_scores: list[float]) -> float:
    """
    Score a user based on the problems they have solved.
    Higher score = solved harder or more “exclusive” problems.
    """
    problem_scores = sorted(problem_scores, reverse=True)
    total_score = 0.0
    for i, score in enumerate(problem_scores):
        total_score += score / (i + 1)
    return total_score

def build(users: list[int]):
    username = os.getenv("CSES_USERNAME")
    password = os.getenv("CSES_PASSWORD")

    cses_instance = Cses(username, password)
    problems = cses_instance.get_problems()

    os.makedirs("data", exist_ok=True)

    # assign leaderboard score to each problem
    ld_score = {}
    for problem in problems:
        ld_score[problem.problem_id] = 0

    leaderboard = cses_instance.get_leaderboard(num_pages=3)
    for user_id in leaderboard:
        _solved, unsolved = cses_instance.get_solved_unsolved(user_id)
        for problem_id in unsolved:
            ld_score[problem_id] += 1 / len(unsolved)

    # assign final score to each problem with score_problem function
    problem_score = {}

    for problem in problems:
        problem_score[problem.problem_id] = score_problem(problem, ld_score[problem.problem_id])

    # save problems to csv
    data = [(i.problem_id, i.title, i.solves, i.attempts, i.solves / i.attempts, problem_score[i.problem_id]) for i in problems]
    df = pd.DataFrame(data, columns=["id", "title", "solves", "attempts", "solve_ratio", "score"])

    df.to_csv("data/cses_problems.csv", index=False, encoding="utf-8")

    # fetch all problem stats (leaderboards) and map all users
    users_map = {}

    for problem in problems:
        stats = cses_instance.get_problem_stats(problem.problem_id)
        for user_id, _ in stats[0] + stats[1]:
            if user_id not in users_map:
                users_map[user_id] = 0
            users_map[user_id] += 1

    user_data = [(user_id, cses_instance.get_username(user_id), count) for user_id, count in users_map.items()]
    user_df = pd.DataFrame(user_data, columns=["user_id", "username", "appearances"])

    user_df = user_df.sort_values(by="appearances", ascending=False)

    user_df.to_csv("data/cses_users.csv", index=False, encoding="utf-8")

    # build leaderboard for given users
    users_leaderboard = []

    for user_id in users:
        username = cses_instance.get_username(user_id)
        solved, _unsolved = cses_instance.get_solved_unsolved(user_id)
        problem_scores = [problem_score[i] for i in solved]
        user_score = score_user(problem_scores)
        users_leaderboard.append((user_id, username, user_score, len(solved)))

    leaderboard_df = pd.DataFrame(users_leaderboard, columns=["user_id", "username", "score", "solved_count"])
    leaderboard_df = leaderboard_df.sort_values(by="score", ascending=False)
    leaderboard_df.to_csv("data/cses_leaderboard.csv", index=False, encoding="utf-8")

    print("Total requests made:", cses_instance.fetcher.get_num_requests())






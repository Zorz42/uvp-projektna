from .cses import Cses
import pandas as pd
import os

def build():
    cses_instance = Cses()
    problems = cses_instance.list_problems()

    ratios = [(i.id, i.title, i.solves, i.attempts, i.solves / i.attempts) for i in problems]

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame(ratios, columns=["id", "title", "solves", "attempts", "solve_ratio"])

    df.to_csv("data/cses_problems.csv", index=False, encoding="utf-8")





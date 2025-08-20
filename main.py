from cses import Cses

if __name__ == "__main__":
    cses = Cses()
    problems = cses.list_problems()

    for problem in problems[:20]:
        print(problem)

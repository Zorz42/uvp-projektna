from .cses import Cses

def build():
    cses_instance = Cses()
    problems = cses_instance.list_problems()

    ratios = [(i.problem_id, i.title, i.solves / i.attempts) for i in problems]
    ratios.sort(key=lambda x: x[2], reverse=True)

    print()
    print("Best solve ratios:")
    for problem_id, title, ratio in ratios[:10]:
        print(f"{problem_id:>4} {title:<50} {ratio:.2%}")

    ratios.sort(key=lambda x: x[2], reverse=False)
    print()
    print("Worst solve ratios:")
    for problem_id, title, ratio in ratios[:10]:
        print(f"{problem_id:>4} {title:<50} {ratio:.2%}")

    solves = [(i.problem_id, i.title, i.solves) for i in problems]
    solves.sort(key=lambda x: x[2], reverse=True)
    print()
    print("Most solved problems:")
    for problem_id, title, solves_count in solves[:10]:
        print(f"{problem_id:>4} {title:<50} {solves_count:>6} solves")

    solves.sort(key=lambda x: x[2], reverse=False)
    print()
    print("Least solved problems:")
    for problem_id, title, solves_count in solves[:10]:
        print(f"{problem_id:>4} {title:<50} {solves_count:>6} solves")



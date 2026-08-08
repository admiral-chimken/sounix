import math


COMMAND = "math"


def run(args):
    if not args:
        return (
            "Sounix Math\n\n"
            "Examples:\n"
            "math sqrt 144\n"
            "math square 12\n"
            "math cube 5\n"
            "math circle area 5"
        )

    parts = args.lower().split()

    try:
        if parts[0] == "sqrt" and len(parts) == 2:
            number = float(parts[1])
            return f"Sounix: √{number} = {math.sqrt(number)}"

        if parts[0] == "square" and len(parts) == 2:
            number = float(parts[1])
            return f"Sounix: {number}² = {number ** 2}"

        if parts[0] == "cube" and len(parts) == 2:
            number = float(parts[1])
            return f"Sounix: {number}³ = {number ** 3}"

        if parts[:2] == ["circle", "area"] and len(parts) == 3:
            radius = float(parts[2])
            area = math.pi * radius ** 2

            return (
                "Sounix Geometry\n\n"
                f"Radius: {radius}\n"
                f"Area: {area}"
            )

        return (
            "Sounix: I don't understand that math command yet.\n\n"
            "Try:\n"
            "math sqrt 144\n"
            "math square 12\n"
            "math cube 5\n"
            "math circle area 5"
        )

    except ValueError:
        return "Sounix: Please enter a valid number."

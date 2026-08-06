from ai import respond


def main():
    print("=== Sounix v0.2 ===")
    print("Type 'help' to view commands.")

    while True:
        try:
            user = input("\nYou: ").strip()

            if not user:
                continue

            if user.lower() in {"exit", "quit"}:
                print("Sounix: Goodbye!")
                break

            answer = respond(user)
            print(answer)

        except KeyboardInterrupt:
            print("\nSounix: Goodbye!")
            break

        except EOFError:
            print("\nSounix: Goodbye!")
            break


if __name__ == "__main__":
    main()

from sys import argv

LETTER_TO_DIGIT = {
    **dict.fromkeys("abc", "2"),
    **dict.fromkeys("def", "3"),
    **dict.fromkeys("ghi", "4"),
    **dict.fromkeys("jkl", "5"),
    **dict.fromkeys("mno", "6"),
    **dict.fromkeys("pqrs", "7"),
    **dict.fromkeys("tuv", "8"),
    **dict.fromkeys("wxyz", "9"),
}

def phone_to_word(text: str) -> str:
    return "".join(LETTER_TO_DIGIT.get(ch.lower(), ch) for ch in text)

def main() -> None:
    try:
        raw_num = argv[1]
        print(phone_to_word(raw_num))
    except IndexError:
        print("Sorry, there was an error!")

if __name__ == "__main__":
    main()
def parse_number(value: str, base: int):
    value = value.strip().lower().replace(" ", "").replace("_", "")

    valid_chars = {
        2: "01",
        8: "01234567",
        16: "0123456789abcdef",
    }

    if not value:
        raise ValueError("입력값이 비어 있습니다.")

    if any(char not in valid_chars[base] for char in value):
        raise ValueError(f"{base}진수에 맞지 않는 문자가 포함되어 있습니다.")

    bit_width = {
        2: len(value),
        8: len(value) * 3,
        16: len(value) * 4,
    }[base]

    return int(value, base), bit_width


def select_base(name: str) -> int:
    types = {
        "bin": 2,
        "binary": 2,
        "2": 2,
        "oct": 8,
        "octal": 8,
        "8": 8,
        "hex": 16,
        "16": 16,
    }

    number_type = input(f"{name} 진법 선택 (BIN/OCT/HEX): ").strip().lower()

    if number_type not in types:
        raise ValueError("진법은 BIN, OCT, HEX 중에서 선택해 주세요.")

    return types[number_type]


def main():
    try:
        base_a = select_base("첫 번째 값")
        a_input = input("첫 번째 값 입력: ")

        base_b = select_base("두 번째 값")
        b_input = input("두 번째 값 입력: ")

        a, width_a = parse_number(a_input, base_a)
        b, width_b = parse_number(b_input, base_b)

        result = a ^ b
        width = max(width_a, width_b)

        print("\nXOR 결과")
        print("BIN :", format(result, f"0{width}b"))
        print("HEX :", format(result, f"0{(width + 3) // 4}x"))
        print("OCT :", format(result, f"0{(width + 2) // 3}o"))
        print("DEC :", result)

    except ValueError as error:
        print("오류:", error)


if __name__ == "__main__":
    main()
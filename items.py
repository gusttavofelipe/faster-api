import json
import random


def generate_items(qtd: int, arquivo: str = "items.txt"):
    items = [{"age": random.randint(18, 60), "name": f"user_{i+1}"} for i in range(qtd)]
    data = {"items": items}

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Done.")


if __name__ == "__main__":
    generate_items(50000)

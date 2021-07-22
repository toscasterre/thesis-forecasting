def iterate_dict(dictio: dict):
    yield from dictio.items()


if __name__ == "__main__":
    mydic = {"a": 1, "b": 2, "c": 3}

    print(iterate_dict(mydic))

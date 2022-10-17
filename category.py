class Seed():

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.seed = data.get("seed")
        self.version = data.get("version")

    def edit_name(self, name: str):
        self.name = name

    def edit_seed(self, seed: int):
        self.seed = seed

    def edit_version(self, version: str):
        self.version = version

    def edit_data(self, new_data: dict):
        self.name = new_data.get("name")
        self.seed = new_data.get("seed")
        self.version = new_data.get("version")

    def to_json(self):
        return {
            "name": self.name,
            "seed": self.seed,
            "version": self.version
        }


class Category():

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.id = data.get("channel")
        self.faq = data.get("faq").replace("\\n", "\n")
        self.seeds = [Seed(seed) for seed in data.get("seeds")]

    def edit_faq(self, faq: str):
        self.faq = faq

    def edit_name(self, name: str):
        self.name = name

    def get_seed_index(self, seed_id: str):
        try: seed_id = int(seed_id)
        except ValueError: return None
        try: i = [seed.seed for seed in self.seeds].index(seed_id)
        except ValueError: return None
        return i

    def get_seed(self, seed_id: str):
        try: seed_id = int(seed_id)
        except ValueError: return None
        try: i = [seed.seed for seed in self.seeds].index(seed_id)
        except ValueError: return None
        return self.seeds[i]

    def add_seed(self, seed_data):
        self.seeds.append(Seed(seed_data))

    def remove_seed(self, seed_id: str):
        try: seed_id = int(seed_id)
        except ValueError: return None
        i = self.get_seed_index(seed_id)
        return self.seeds.pop(i).seed if i is not None else None

    def edit_seed(self, seed_id: str, data: dict):
        try: seed_id = int(seed_id)
        except ValueError: return None
        seed = self.get_seed(seed_id)
        if seed == None: return None
        seed.edit_name(data.get("name"))
        seed.edit_seed(data.get("seed"))
        seed.edit_version(data.get("version"))
        return seed.seed


    def to_json(self):
        return {
            "name": self.name,
            "channel": self.id,
            "faq": self.faq,
            "seeds": [seed.to_json() for seed in self.seeds]
        }

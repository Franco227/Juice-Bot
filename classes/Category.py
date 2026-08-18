from classes.Seed import Seed


class Category():

    def __init__(self, data: dict):
        self.name: str = data.get("name", "Nameless Category")
        self.id: int = data.get("channel", 0)
        self.faq: str = data.get("faq", "FAQ not available yet").replace("\\n", "\n")
        self.seeds = [Seed(seed) for seed in data.get("seeds", [])]

    def __str__(self) -> str:
        return f"<Category  id={self.id}  name={self.name}  seeds_nb={len(self.seeds)}>"


    def edit_name(self, name: str):
        self.name = name

    def edit_faq(self, faq: str):
        self.faq = faq

    def get_seed(self, seed: str) -> Seed | None:
        for seed_object in self.seeds:
            if seed_object.seed == seed:
                return seed_object
        return None

    def add_seed(self, seed_data: dict):
        self.seeds.append(Seed(seed_data))

    def remove_seed(self, seed: str):
        self.seeds = [seed_object for seed_object in self.seeds if seed_object.seed != seed]

    def edit_seed(self, seed: str, new_data: dict):
        found_seed = self.get_seed(seed)
        if found_seed is None:
            return
        found_seed.edit_data(new_data)

    def seed_sortkey(self, seed: Seed) -> list:
        sortkey = []
        version = seed.version.split('-')[0].split('.')
        sortkey.extend(list(map(int, version[:2])))
        if len(version) == 1 or version[1] == "x":
            sortkey.extend([0, 0])
        elif len(version) == 2 or version[2].lower() == 'x':
            sortkey.append(0)
        else:
            sortkey.append(int(version[2]))
        sortkey.append(seed.name)
        return sortkey


    def sort_seeds(self):
        self.seeds = sorted(self.seeds, key=self.seed_sortkey)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "channel": self.id,
            "faq": self.faq,
            "seeds": [seed.to_json() for seed in self.seeds]
        }

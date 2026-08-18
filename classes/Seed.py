class Seed():

    def __init__(self, data: dict):
        self.name: str = data.get("name", "Nameless Seed")
        self.seed: str = data.get("seed", "<no assigned seed>")
        self.version: str = data.get("version", "0.0.0")

    def __str__(self) -> str:
        return f"<Seed  name={self.name}  seed={self.seed}  version={self.version}>"


    def edit_data(self, new_data: dict):
        self.name = new_data.get("name", "Nameless Seed")
        self.seed = new_data.get("seed", "<no assigned seed>")
        self.version = new_data.get("version", "0.0.0")

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "seed": self.seed,
            "version": self.version
        }
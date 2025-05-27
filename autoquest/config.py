import yaml

# Load configuration from config.yaml
def load_config(path="autoquest/config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

config = load_config()

# Access like: config["model_path"], config["llm_context_size"], etc.

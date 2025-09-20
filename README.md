## Create a new project

```sh
# Install python3 and create a new project.

python3 --version
mkdir my_agent
cd my_agent
python3 -m venv .venv
source .venv/bin/activate
which python
# install langgraph and langchain

pip install --pre langgraph langchain langchain-openai
pip install "langgraph-cli[inmem]"

# run the agent
langgraph dev
```

### Env with UV

```sh
# Install uv

curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version

# deactivate the virtual environment
deactivate
rm -rf .venv

## init
uv init
uv venv

# add dependencies
uv add --pre langgraph langchain langchain-openai
uv add "langgraph-cli[inmem]" --dev

# run the agent
uv run langgraph dev

# add ipykernel for jupyter
uv add ipykernel --dev
uv add grandalf --dev

# install the project
uv pip install -e .
```

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["*"]
```

- https://mermaidviewer.com/editor




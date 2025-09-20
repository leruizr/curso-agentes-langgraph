from typing import TypedDict

class State(TypedDict):
    customer_name: str
    my_age: int


def node_1(state: State):
    if state.get("customer_name") is None:
        return {
            "customer_name": "John Doe"
        }
    return {
        "my_age": 20
    }

from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("node_1", node_1)

builder.add_edge(START, 'node_1')
builder.add_edge('node_1', END)

agent = builder.compile()
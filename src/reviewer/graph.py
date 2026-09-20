from langgraph.graph import END, START, StateGraph

from .nodes.fetch import fetch_node
from .nodes.reviewer import review_node
from .state import ReviewState


def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("fetch", fetch_node)
    graph.add_node("review", review_node)

    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", "review")
    graph.add_edge("review", END)

    return graph.compile()
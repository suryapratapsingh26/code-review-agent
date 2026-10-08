from langgraph.graph import END, START, StateGraph

from .nodes.fetch import fetch_node
from .nodes.reviewer import triage_node, security_node, bug_node, maintainability_node
from .state import ReviewState


def route_to_reviewers(state: ReviewState) -> list[str]:
    chosen = state["reviewers_to_run"]
    return chosen if chosen else [END]


def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("fetch", fetch_node)
    graph.add_node("triage", triage_node)
    graph.add_node("security", security_node)
    graph.add_node("bug", bug_node)
    graph.add_node("maintainability", maintainability_node)

    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", "triage")
    graph.add_conditional_edges(
        "triage",
        route_to_reviewers,
        ["security", "bug", "maintainability", END],
    )
    graph.add_edge("security", END)
    graph.add_edge("bug", END)
    graph.add_edge("maintainability", END)

    return graph.compile()
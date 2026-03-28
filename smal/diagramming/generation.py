from graphviz import Digraph
from smal.schemas.smal_file import SMALFile

def generate_state_machine_svg(smal_path: str, output_svg_path: str) -> None:
    smal = SMALFile.from_file(smal_path)
    dot = Digraph(
        name=smal.machine,
        format="svg",
        graph_attr={"rankdir": "LR", "fontsize": "10", "fontname": "Arial"},
        node_attr={"shape": "ellipse", "style": "filled", "fillcolor": "#f0f0f0"},
        edge_attr={"fontsize": "9"},
    )

    # Add states
    for state in smal.states:
        dot.node(state.name)

    # Add transitions
    for t in smal.transitions:
        label = f"{t.trigger_evt} / {t.action}"
        if t.landing_state_entry_evt:
            label += f" → {t.landing_state_entry_evt}"
        dot.edge(t.trigger_state, t.landing_state, label=label)

    dot.render("machine.svg", cleanup=True)

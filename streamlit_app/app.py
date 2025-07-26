import streamlit as st
import sys
import os
import plotly.graph_objects as go
import numpy as np
import hashlib

# No longer need to modify the path
from consistent_hash.consistent_hashing import ConsistentHashRing

st.set_page_config(layout="wide")

def plot_hash_ring_plotly(ring: ConsistentHashRing, key_to_show: str | None = None, nodes_for_key: list | None = None):
    """
    Visualizes the hash ring, nodes, and a specific key using Plotly.
    """
    fig = go.Figure()

    # Create a color map for physical nodes
    unique_nodes = sorted(list(ring.nodes))
    node_colors = {node: f'hsl({i * 360 / len(unique_nodes)}, 80%, 50%)' for i, node in enumerate(unique_nodes)}


    # Ring circumference for annotations
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=-1, y0=-1, x1=1, y1=1,
        line_color="lightgray",
        line_width=2,
        layer="below"
    )

    # Plot virtual nodes
    for h in ring.sorted_keys:
        angle = (h / (2**256 - 1)) * 2 * np.pi
        x = np.cos(angle)
        y = np.sin(angle)
        node = ring.ring[h]
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(color=node_colors.get(node, 'gray'), size=10),
            name=node,
            legendgroup=node,
            showlegend=unique_nodes.index(node) == 0, # Show legend only for the first occurrence
            hoverinfo='text',
            text=f"Virtual Node<br>Hash: {h}<br>Owner: {node}"
        ))

    # Plot the key to be hashed
    if key_to_show:
        key_hash = ring._hash(key_to_show)
        angle = (key_hash / (2**256 - 1)) * 2 * np.pi
        x_key = np.cos(angle)
        y_key = np.sin(angle)
        fig.add_trace(go.Scatter(
            x=[x_key],
            y=[y_key],
            mode='markers',
            marker=dict(color='red', size=15, symbol='x'),
            name=f"Key: {key_to_show}",
            hoverinfo='text',
            text=f"Key: {key_to_show}<br>Hash: {key_hash}"
        ))

    # Highlight nodes for the key
    if nodes_for_key:
        for node in nodes_for_key:
            # Find a representative virtual node to highlight
            for i in range(ring.virtual_nodes):
                vkey_hash = ring._hash(f"{node}:{i}")
                if vkey_hash in ring.ring:
                    angle = (vkey_hash / (2**256 - 1)) * 2 * np.pi
                    x_node = np.cos(angle)
                    y_node = np.sin(angle)
                    fig.add_trace(go.Scatter(
                        x=[x_node],
                        y=[y_node],
                        mode='markers',
                        marker=dict(size=14, color='rgba(0,0,0,0)', line=dict(color='red', width=3)),
                        name=f"Assigned Node: {node}",
                        showlegend=False,
                        hoverinfo='none'
                    ))
                    break

    fig.update_layout(
        width=700,
        height=700,
        xaxis=dict(visible=False, range=[-1.2, 1.2]),
        yaxis=dict(visible=False, range=[-1.2, 1.2], scaleanchor="x", scaleratio=1),
        showlegend=True,
        legend_title_text='Physical Nodes',
        margin=dict(t=50, b=50, l=50, r=50),
        title=dict(text="Consistent Hash Ring", x=0.5)
    )

    return fig


def main():
    st.title("Consistent Hashing Visualization")

    # --- Session State Initialization ---
    if 'hash_ring' not in st.session_state:
        st.session_state.hash_ring = ConsistentHashRing(nodes=['node1', 'node2', 'node3'])
    if 'key_to_find' not in st.session_state:
        st.session_state.key_to_find = "my_special_key"

    ring: ConsistentHashRing = st.session_state.hash_ring

    # --- Sidebar for Controls ---
    st.sidebar.title("Ring Configuration")

    virtual_nodes = st.sidebar.slider("Virtual Nodes per Physical Node", 1, 200, ring.virtual_nodes)
    replication_factor = st.sidebar.slider("Replication Factor", 1, 10, ring.replication_factor)

    if virtual_nodes != ring.virtual_nodes or replication_factor != ring.replication_factor:
        current_nodes = list(ring.nodes)
        st.session_state.hash_ring = ConsistentHashRing(
            nodes=current_nodes,
            virtual_nodes=virtual_nodes,
            replication_factor=replication_factor
        )
        st.rerun()


    st.sidebar.header("Manage Nodes")
    node_name = st.sidebar.text_input("Node Name", "node4")

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Add Node"):
        if node_name:
            ring.add_node(node_name)
            st.sidebar.success(f"Added node: {node_name}")
        else:
            st.sidebar.warning("Node name cannot be empty.")

    if col2.button("Remove Node"):
        if node_name in ring.nodes:
            ring.remove_node(node_name)
            st.sidebar.success(f"Removed node: {node_name}")
        else:
            st.sidebar.error(f"Node '{node_name}' not found.")

    # --- Main Content ---
    st.header("Hash Ring Visualization")

    key_to_find = st.text_input("Enter a key to locate on the ring:", st.session_state.key_to_find)
    st.session_state.key_to_find = key_to_find

    nodes_for_key = []
    if key_to_find:
        nodes_for_key = ring.get_nodes_for_key(key_to_find)
        st.info(f"Key '{key_to_find}' is mapped to node(s): **{', '.join(nodes_for_key)}**")


    # Plot the ring
    fig = plot_hash_ring_plotly(ring, key_to_find, nodes_for_key)
    st.plotly_chart(fig)


    # --- Ring State Details ---
    with st.expander("Show Ring State Details"):
        st.subheader("Current Physical Nodes")
        st.write(sorted(list(ring.nodes)))

        st.subheader("Sorted Virtual Node Hashes")
        st.json({h: ring.ring[h] for h in ring.sorted_keys})

if __name__ == "__main__":
    main() 
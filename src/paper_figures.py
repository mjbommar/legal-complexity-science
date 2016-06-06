"""
@date 20160605
"""

# Imports
import copy
import gc
import glob
import igraph
import lxml.etree
import lxml.html
import multiprocessing
import os
import pandas
import pickle
import re
import zipfile

# Setup matplotlib and seaborn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines
import seaborn
seaborn.set_style("darkgrid")

# NLTK imports
import nltk
from nltk.corpus import stopwords
stopwords = stopwords.words('english')

# Project imports
from us_code_parser import CodeSnapshot

# Regexs
RE_YEAR = re.compile("([0-9]{4,})", re.UNICODE)



def is_section(s):
    return "Sec." in s["itempath"].split("/").pop()


def get_tokens(s):
    tokens = nltk.word_tokenize(s["statute"])
    return tokens


def parse_sections(sections):
    # Store all section data
    section_data = []

    # Iterate over all sections
    for section in sections:
        # Title and section
        title_field = section["title"] if "title" in section else None
        section_field = section["section"] if "section" in section else None
        expcite_field = section["expcite"] if "expcite" in section else None
        itempath_field = section["itempath"] if "itempath" in section else None

        # Get tokens
        tokens = get_tokens(section)
        section_row = (expcite_field, itempath_field, title_field, section_field,
                       is_section(section), len(tokens), len(set(tokens)))
        section_data.append(section_row)

    # Convert to DF
    section_df = pandas.DataFrame(section_data, columns=["expcite", "itempath", "title", "section",
                                                         "is_section", "num_tokens", "num_unique_tokens"])
    return section_df


def generate_section_data(base_pickle_path="data/pickle/", base_output_path="data/outputs/"):
    """
    Generate section CSV data from pickle files.
    :param base_pickle_path: base path to pickle files
    :return:
    """
    # Aggregate across all years
    all_section_df = pandas.DataFrame()
    
    # Get list of years
    pickle_file_list = sorted(glob.glob(os.path.join(base_pickle_path, "*.pickle")))
    for pickle_file_name in pickle_file_list:
        # Load pickle data
        print(pickle_file_name)
        year = RE_YEAR.findall(pickle_file_name).pop()
        with open(pickle_file_name, "rb") as pickle_file:
            pickle_data = pickle.load(pickle_file)

        # Parse
        section_df = parse_sections(pickle_data.sections)
        section_df.to_csv(os.path.join(base_output_path, "section_data_{0}.csv".format(year)),
                      index=False, encoding="utf-8")

        # Setup all section data frame
        section_df.loc[:, "year"] = year
        if all_section_df.shape[0] <= 0:
            all_section_df = section_df.copy()
        else:
            all_section_df = all_section_df.append(section_df.copy())

    # Output sections and tokens per year
    section_ts = all_section_df.groupby(["year"])["is_section"].sum()
    section_ts.to_csv("paper/section_ts.csv")
    tokens_ts = all_section_df.groupby(["year"])["num_tokens"].sum()
    tokens_ts.to_csv("paper/token_ts.csv")
    

def generate_structural_figure(code_snapshot):
    """
    Generate a circular graph figure representing the structure of the US Code.
    """
    # Get edgelist
    edge_list = [(code_snapshot.nodes.index(e[0]),
                  code_snapshot.nodes.index(e[1])) for e in code_snapshot.edges]

    # Create graph and layout
    g = igraph.Graph(edge_list)
    layout = g.layout_reingold_tilford_circular()

    # Get palette and apply colors
    p = seaborn.cubehelix_palette(8, start=2, rot=0, dark=0, light=.95, reverse=True)
    title_list = list(set([n.split("/")[1] if n.count("/") > 1 else None for n in code_snapshot.nodes]))
    cmap = seaborn.cubehelix_palette(len(title_list))
    node_color = [cmap.as_hex()[title_list.index(n.split("/")[1])] if n.count("/") > 1 else "#000000" for n in code_snapshot.nodes]

    # Plot
    x, y = zip(*layout)

    # Setup figure
    f = plt.figure(figsize=(16, 16))
    ax = f.add_subplot(111, axisbg='#ffffff')
    ax.grid(b=False, axis="both")
    ax.set_axis_off()

    # Draw nodes
    ax.scatter(x, y, marker='.', alpha=0.25, s=0.25, color=node_color)

    # Add edges
    for node_a, node_b in edge_list:
            ax.add_line(matplotlib.lines.Line2D([layout[node_a][0], layout[node_b][0]],
                                                                        [layout[node_a][1], layout[node_b][1]],
                                                                        linewidth=0.1,
                                                                        alpha=0.15,
                                                                        color=node_color[node_b]))
    
    # Draw canvas
    f.canvas.draw()
    plt.savefig("paper/us-code-structure-network.png", bbox_inches="tight")    
        
if __name__ == "__main__":
    # Output section data
    generate_section_data()

    # Output structural figure
    pickle_file_name = "data/pickle/2014.pickle"
    with open(pickle_file_name, "rb") as pickle_file:
        code_snapshot = pickle.load(pickle_file)
        generate_structural_figure(code_snapshot)

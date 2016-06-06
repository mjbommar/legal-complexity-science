"""
Replication material for 'Complexity Science and Legal Systems' Submitted to Science (June 2016)
# J.B. Ruhl, Daniel Martin Katz, Michael J. Bommarito II

@date 20160605
@author Michael J Bommarito <mike@lexpredict.com>
"""

# Imports
import copy
import pickle
import datetime
import gc
import glob
import lxml.etree
import lxml.html
import multiprocessing
import os
import re
import zipfile

# Regular expresions
RE_YEAR = re.compile("([0-9]{4,})", re.UNICODE)
RE_TITLE = re.compile("title ([0-9]+)", re.IGNORECASE | re.UNICODE)
RE_SECTION = re.compile("sec. (.+)", re.IGNORECASE | re.UNICODE)


class CodeSnapshot(object):
    """
    Code snapshot object, which stores data about the
    U.S. Code at a given point in time.
    """

    def __init__(self, date, sections, nodes, edges, possible_cites, reference_list):
        """
        Constructor
        :param date:  datetime.date, that which snapshot represents
        :param sections: section list
        :param nodes: node list
        :param edges: edge list
        :param possible_cites: potential citations
        :param reference_list: references
        :return:
        """
        #  Set fields
        self.date = date
        self.sections = sections
        self.nodes = nodes
        self.edges = edges
        self.possible_cites = possible_cites
        self.reference_list = reference_list


def parse_title_doc(html_buffer):
    """
    Parse an HTML document corresponding to a US Code Title document,
    e.g., 1994usc41.htm.
    :param html_buffer: HTML buffer
    """
    # Setup lxml doc
    html_doc = lxml.html.fromstring(html_buffer)

    # Setup title data structures
    section = {"itempath": None,
               "expcite": "",
               "head": "",
               "statute": ""}
    section_list = []
    current_section = None

    # Iterate over all elements
    for e in html_doc.getiterator():
        # Check if we have a comment
        if e.tag == lxml.etree.Comment:
            # Check the page
            comment_type = e.text.lower().strip()

            if comment_type.startswith("itempath:"):
                # Setup item path
                if not section["itempath"]:
                    section["itempath"] = copy.copy(e.text.split(":", 1)[1])
                else:
                    # Append
                    section_list.append(copy.copy(section))
                    del section
                    section = {"itempath": copy.copy(e.text.split(":", 1)[1]),
                               "expcite": "",
                               "head": "",
                               "statute": ""}
            elif comment_type.startswith("expcite:"):
                # Setup explicit cite
                section["expcite"] = copy.copy(e.text.split(":", 1)[1])
                if "title" in section["expcite"].lower():
                    section["title"] = section["expcite"].strip().split("-")[0].split()[-1]

                if "Sec." in section["expcite"]:
                    section["section"] = section["expcite"].strip().split()[-1]
            elif comment_type.startswith("field-start:statute"):
                current_section = "statute"
            elif comment_type.startswith("field-end:statute"):
                current_section = None
            elif comment_type.startswith("field-start:head"):
                current_section = "head"
            elif comment_type.startswith("field-end:head"):
                current_section = None
            else:
                pass

        if current_section and e.tag is not lxml.etree.Comment:
            if current_section in ["statute"]:
                section["statute"] += lxml.etree.tostring(e, method="text", encoding="utf-8").decode("utf-8")
            elif current_section in ["head"]:
                section["head"] += lxml.etree.tostring(e, method="text", encoding="utf-8").decode("utf-8")

    return section_list


def parse_year_zip(zip_file_path, num_workers=1):
    """
    Parse a US Code yearly zip release.
    :param zip_file_path: path to zip file
    :param num_workers: number of workers, one per title
    """
    # Setup pool
    pool = multiprocessing.Pool(num_workers)

    # Open file
    code_zip = zipfile.ZipFile(zip_file_path)
    code_zip_files = [file_name for file_name in code_zip.namelist()]

    # Iterate over all files
    title_doc_list = [code_zip.open(code_zip_file).read()
                      for code_zip_file in code_zip_files]
    section_list_pieces = pool.map(parse_title_doc, title_doc_list)
    section_list = [i for l in section_list_pieces for i in l]

    return section_list


def build_graph_structural(sections):
    """
    Build the hierarchical/structural graph from a
    set of sections.
    :param sections: section list across all titles
    """
    # Extract paths
    all_paths = [s["itempath"] for s in sections]

    # Initialize nodes/edges
    nodes = []
    edges = []

    # Iterate over all paths
    for path in all_paths:
        # Split into tokens and add all edges/nodes
        tokens = ("ROOT/" + path.strip("/")).strip().split("/")
        for i in range(1, len(tokens)):
            node_a = "/".join(tokens[0:i])
            if node_a == "":
                node_a = "ROOT"
            node_b = "/".join(tokens[0:(i + 1)])
            nodes.extend([node_a, node_b])
            edges.append((node_a, node_b))

    # Unique to lists
    nodes = sorted(list(set(nodes)))
    edges = sorted(list(set(edges)))

    return nodes, edges


def build_possible_citation_list(sections):
    """
    Build a list of possible citations to title/section
    pairs from a set of sections.
    :param sections: section list across all titles
    """
    # Combine list of titles and sections
    title_section_cites = [(s["expcite"].split("-")[0].replace("TITLE", "").strip(),
                            s["itempath"].split("/")[-1].replace("Sec.", "").strip())
                           for s in sections if "/Sec." in s["itempath"]]
    return title_section_cites


def get_title_section(expcite):
    """
    Get title and section from expcite.
    :param expcite: expcite value from section
    """
    # Ignore empties
    if len(expcite.strip()) == 0:
        return None, None

    # Split tokens
    tokens = expcite.split("!@!")

    try:
        title = RE_TITLE.findall(tokens[0])[0].strip()
    except:
        title = tokens[0].strip()

    if "Sec." in expcite:
        section = RE_SECTION.findall(tokens[-1])[0].strip()
    else:
        section = None

    return title, section


def get_reference_list(sections):
    """"
    Get the list of all citation references
    between sections of the code.
    :param sections: section list across all titles
    """
    # Setup citation regex
    re_list = [re.compile("section ([0-9]+[0-9a-z\-]*) of (this title)", re.IGNORECASE | re.UNICODE),
               re.compile("section ([0-9]+[0-9a-z\-]*) of (title [0-9a-z]{1,3})", re.IGNORECASE | re.UNICODE),
               re.compile("sections ([0-9]+[0-9a-z\-, ]*) of (this title)", re.IGNORECASE | re.UNICODE),
               re.compile("sections ([0-9]+[0-9a-z\-, ]*) of (title [0-9a-z]{1,3})", re.IGNORECASE | re.UNICODE),
               re.compile("§ ([0-9]+[0-9a-z\-, ]*) of (this title)", re.IGNORECASE | re.UNICODE),
               re.compile("§ ([0-9]+[0-9a-z\-, ]*) of (title [0-9a-z]{1,3})", re.IGNORECASE | re.UNICODE),
               ]

    re_number = re.compile("([0-9]+[0-9a-z\-]*)", re.IGNORECASE | re.UNICODE)

    # Initialize reference list
    reference_list = []

    # Iterate through sections
    for section in sections:
        # Get current section and title
        title_a, section_a = get_title_section(section["expcite"])

        # Iterate through regexs
        for f in re_list:
            # Iterate through matches
            for m in f.findall(section["statute"]):
                # Parse title cite
                try:
                    title_b = title_a if "this title" in m[1] else re_number.findall(m[1])[0]
                except Exception:
                    continue

                # Split tokens in sections
                for section_b in re_number.findall(m[0]):
                    reference_list.append((title_a, section_a, title_b, section_b))

    return reference_list


def generate_pickle_files(base_zip_path="data/input/", base_output_path="data/pickle/"):
    """
    Generate pickle files encoding all US Code snapshots.
    :param base_zip_path: base path to folder with ZIP files
    :param base_output_path: location to store pickle file outputs
    :return:
    """

    # Get ZIP files
    zip_file_list = sorted(glob.glob(os.path.join(base_zip_path, "*.zip")))

    # Parse each snapshot
    for zip_file_name in zip_file_list:
        # Get year
        year = RE_YEAR.findall(zip_file_name).pop()
        date = datetime.date(int(year), 1, 1)
        print(year)

        # Parse sections
        sections = parse_year_zip(zip_file_name)

        # Get graphs, cites, and references
        nodes, edges = build_graph_structural(sections)
        possible_cites = build_possible_citation_list(sections)
        reference_list = get_reference_list(sections)

        # Setup class and output to pickle file
        c = CodeSnapshot(date, sections, nodes, edges, possible_cites, reference_list)
        pickle_file_name = os.path.join(base_output_path, "{0}.pickle".format(year))
        with open(pickle_file_name, "wb") as pickle_file:
            pickle.dump(c, pickle_file)

        # Cleanup for low-memory machines
        del sections
        del nodes
        del edges
        del possible_cites
        del reference_list
        del c
        gc.collect()


if __name__ == "__main__":
    # Generate pickle files
    generate_pickle_files("data/input/", "data/pickle/")

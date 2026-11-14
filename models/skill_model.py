"""Rule-based skill taxonomy + relationship graph (NetworkX). Transparent baseline, not a trained model."""
import functools, re
import networkx as nx
from utils.helpers import load_csv, split_pipe

AMBIGUOUS_NAMES = {"R", "Excel"}  # match only via explicit synonyms ("r programming", "ms excel")


class SkillTaxonomy:
    def __init__(self):
        df = load_csv("skills.csv").fillna("")
        self.df = df
        self.names = list(df.skill)
        self.category = dict(zip(df.skill, df.category))
        self.synonyms = {r.skill: split_pipe(r.synonyms) for r in df.itertuples()}
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.names)
        for r in df.itertuples():
            for rel in split_pipe(r.related):
                if rel in self.category: self.graph.add_edge(r.skill, rel)
        self.patterns = {}
        for s in self.names:
            terms = ([] if s in AMBIGUOUS_NAMES else [s]) + self.synonyms[s]
            terms = sorted({t for t in terms if t}, key=len, reverse=True)
            if terms:
                alt = "|".join(re.escape(t) for t in terms)
                self.patterns[s] = re.compile(rf"(?<![A-Za-z0-9+#.]){'(?:' + alt + ')'}(?![A-Za-z0-9+#])", re.I)

    def neighbors(self, skill):
        return set(self.graph.neighbors(skill)) if skill in self.graph else set()

    def same_category(self, skill):
        c = self.category.get(skill)
        return {s for s, cat in self.category.items() if cat == c and s != skill}


@functools.lru_cache(maxsize=1)
def get_taxonomy() -> SkillTaxonomy:
    return SkillTaxonomy()

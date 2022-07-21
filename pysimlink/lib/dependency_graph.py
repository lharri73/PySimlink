class DepGraph:
    """
    Based on a simple map, this class holds the name of each _model and
    contains a set with all of the dependent models (only needed when _model
    references are present)
    """
    def __init__(self):
        self.dep_map = {}

    def add_dependency(self, lib: str, dependents: list[str]):
        """Add a dependency to the graph

        Args:
            lib: name of the _model to add
            dependents: list of all dependents
        """
        if lib not in self.dep_map:
            self.dep_map.update({lib: set(dependents)})
        else:
            self.dep_map.update({lib: self.dep_map[lib].union(dependents)})

    def __contains__(self, obj):
        return obj in self.dep_map

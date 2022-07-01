class DepGraph:
    def __init__(self):
        self.dep_map = {}

    def add_dependency(self, lib, dependendts):
        if lib not in self.dep_map:
            self.dep_map.update({lib: set(dependendts)})
        else:
            self.dep_map.update({lib: self.dep_map[lib].union(dependendts)})

    def __contains__(self, obj):
        return obj in self.dep_map

from dataclasses import dataclass


@dataclass
class Field:
    type: str
    name: str


class Struct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


def parse_struct(lines):
    fields = []
    for i, line in enumerate(lines):
        if i == 0:
            continue
        line = line.strip().split()
        if line[0] == "}":
            struct = Struct(line[1][:-1], fields)
            return struct
        else:
            fields.append(Field(line[0], line[1][:-1]))

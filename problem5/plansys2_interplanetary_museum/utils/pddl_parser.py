import re
import argparse

class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = self._load()

    def _remove_comments(self, text):
        return re.sub(r";.*$", "", text, flags=re.MULTILINE)

    def _tokenize(self, text):
        return re.findall(r"\(|\)|[^\s()]+", text)

    def _parse_sexp(self, tokens):
        if not tokens:
            raise ValueError("Unexpected EOF while parsing PDDL")

        token = tokens.pop(0)

        if token == "(":
            result = []
            while tokens[0] != ")":
                result.append(self._parse_sexp(tokens))
            tokens.pop(0)
            return result

        return token

    def _load(self):
        with open(self.file_path) as f:
            text = self._remove_comments(f.read())

        tokens = self._tokenize(text)
        return self._parse_sexp(tokens)

    def sanitize(self, name: str) -> str:
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

# Domain hierarchy parser needed to expand goal states
class DomainHierarchy(Parser):
    def __init__(self, domain_file):
        self.domain_file = domain_file
        super().__init__(domain_file)

        self.type_parent = self._parse_types()
        self.type_cache = {}

    def _parse_types(self):
        for section in self.tree:
            if isinstance(section, list) and section and section[0] == ":types":
                tokens = section[1:]
                break
        else:
            return {}

        mapping = {}
        current = []

        i = 0
        while i < len(tokens):
            t = tokens[i]

            if t == "-":
                parent = self.sanitize(tokens[i + 1])

                for c in current:
                    mapping[self.sanitize(c)] = parent

                current = []
                i += 2
            else:
                current.append(self.sanitize(t))
                i += 1

        return mapping

    def get_all_supertypes(self, typ):
        typ = self.sanitize(typ)

        if typ in self.type_cache:
            return self.type_cache[typ]

        result = set()
        current = typ

        while current in self.type_parent:
            parent = self.type_parent[current]
            result.add(parent)
            current = parent

        self.type_cache[typ] = result
        return result

    def expand_type(self, typ):
        typ = self.sanitize(typ)
        return {typ} | self.get_all_supertypes(typ)


# Actual problem parser
class PDDLProblemParser(Parser):
    def __init__(self, problem_file, domain_hierarchy: DomainHierarchy):
        self.problem_file = problem_file
        self.hierarchy = domain_hierarchy
        super().__init__(problem_file)

    # ----------------------------
    def find_section(self, tree, name):
        for item in tree:
            if isinstance(item, list) and item and item[0] == name:
                return item
        return None

    # ----------------------------
    def parse_objects(self, objects_section):
        entries = objects_section[1:]

        instances = []
        current = []

        i = 0
        while i < len(entries):
            token = entries[i]

            if token == "-":
                obj_type = self.sanitize(entries[i + 1])
                
                for obj in current:
                    instances.append((self.sanitize(obj), self.sanitize(obj_type)))

                current = []
                i += 2
            else:
                current.append(token)
                i += 1

        return self._dedup(instances)

    # ----------------------------
    def _dedup(self, lst):
        seen = set()
        out = []
        for x in lst:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    # ----------------------------
    def build_type_index(self, instances):
        type_index = {}
        for name, typ in instances:
            type_index.setdefault(typ, []).append(name)
        return type_index

    def expand_goal(self, expr, type_index):
        if isinstance(expr, str):
            return self.sanitize(expr)

        op = expr[0]

        if op == "and":
            return ["and"] + [self.expand_goal(e, type_index) for e in expr[1:]]

        if op == "or":
            return ["or"] + [self.expand_goal(e, type_index) for e in expr[1:]]

        if op == "forall":
            vars_decl = expr[1]
            body = expr[2]

            var_name = vars_decl[0]
            var_type = self.sanitize(vars_decl[2])

            expanded = []
            for obj in type_index.get(var_type, []):
                expanded.append(self.substitute(body, var_name, obj))

            return ["and"] + [self.expand_goal(e, type_index) for e in expanded]

        return expr

    def substitute(self, expr, var, value):
        if isinstance(expr, str):
            return self.sanitize(value) if expr == var else self.sanitize(expr)

        return [self.substitute(e, var, value) for e in expr]

    def predicate_to_string(self, expr):
        if isinstance(expr, str):
            return self.sanitize(expr)

        return "(" + " ".join(self.predicate_to_string(x) for x in expr) + ")"

    def parse_init(self, init_section):
        predicates = []
        functions = []

        for expr in init_section[1:]:
            if isinstance(expr, list) and expr and expr[0] == "=":
                functions.append(self.predicate_to_string(expr))
            else:
                predicates.append(self.predicate_to_string(expr))

        return predicates, functions

    def flatten_goal(self, goal_section, type_index):
        goal_expr = goal_section[1]
        expanded = self.expand_goal(goal_expr, type_index)
        return self.predicate_to_string(expanded)

    def convert_pddl(self):
        tree = self.tree

        objects_section = self.find_section(tree, ":objects")
        init_section = self.find_section(tree, ":init")
        goal_section = self.find_section(tree, ":goal")

        if not objects_section or not init_section or not goal_section:
            raise ValueError("Missing required PDDL sections")

        instances = self.parse_objects(objects_section)
        predicates, functions = self.parse_init(init_section)
        type_index = self.build_type_index(instances)
        goal = self.flatten_goal(goal_section, type_index)

        lines = []

        # Objects
        for name, typ in instances:
            lines.append(f"set instance {name} {typ}")

        lines.append("")

        # Predicates
        for pred in predicates:
            lines.append(f"set predicate {pred}")

        lines.append("")

        # Functions
        for fn in functions:
            lines.append(f"set function {fn}")

        lines.append("")

        # Goal
        lines.append(f"set goal {goal}")

        return "\n".join(lines)

    def convert_and_write_output(self, output_file):
        content = self.convert_pddl()
        with open(output_file, "w") as f:
            f.write(content)
        return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pddl_dir")
    parser.add_argument("output_file")
    args = parser.parse_args()

    domain = DomainHierarchy(args.pddl_dir + "/domain.pddl")
    problem = PDDLProblemParser(args.pddl_dir + "/problem.pddl", domain)

    problem.convert_and_write_output(args.output_file)

    print(f"Written output to {args.output_file}")
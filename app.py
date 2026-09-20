from flask import Flask, render_template, request
import os
import re
import ast
from difflib import SequenceMatcher


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------------
# ALLOWED FILE TYPES
# -----------------------------------

ALLOWED_EXTENSIONS = {
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".js",
    ".html",
    ".css"
}


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = os.path.splitext(filename)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------------
# TOKENIZE CODE
# -----------------------------------

def tokenize_code(code):

    code_without_comments = re.sub(r"#.*", "", code)
    code_without_comments = code_without_comments.lower()

    tokens = re.findall(
        r"[a-zA-Z_][a-zA-Z0-9_]*|\d+(?:\.\d+)?|"
        r"==|!=|<=|>=|[+\-*/%=<>():,.\[\]{}]",
        code_without_comments
    )

    return tokens


# -----------------------------------
# GET IDENTIFIERS
# -----------------------------------

def get_identifiers(tokens):

    keywords = {
        "and", "as", "assert", "break", "class",
        "continue", "def", "del", "elif", "else",
        "except", "finally", "for", "from", "global",
        "if", "import", "in", "is", "lambda",
        "not", "or", "pass", "raise", "return",
        "try", "while", "with", "yield",
        "print", "input", "range", "len",
        "int", "float", "str"
    }

    identifiers = []

    for token in tokens:

        if re.fullmatch(
            r"[a-zA-Z_][a-zA-Z0-9_]*",
            token
        ):

            if token not in keywords:
                identifiers.append(token)

    return identifiers


# -----------------------------------
# NORMALIZE VARIABLES
# -----------------------------------

def normalize_variables(tokens):

    keywords = {
        "and", "as", "assert", "break", "class",
        "continue", "def", "del", "elif", "else",
        "except", "finally", "for", "from", "global",
        "if", "import", "in", "is", "lambda",
        "not", "or", "pass", "raise", "return",
        "try", "while", "with", "yield",
        "print", "input", "range", "len",
        "int", "float", "str"
    }

    variable_map = {}
    next_variable = 1
    normalized = []

    for token in tokens:

        if re.fullmatch(
            r"[a-zA-Z_][a-zA-Z0-9_]*",
            token
        ):

            if token in keywords:

                normalized.append(token)

            else:

                if token not in variable_map:

                    variable_map[token] = (
                        f"VAR{next_variable}"
                    )

                    next_variable += 1

                normalized.append(
                    variable_map[token]
                )

        else:

            normalized.append(token)

    return normalized


# -----------------------------------
# TOKEN SIMILARITY
# -----------------------------------

def token_similarity(tokens1, tokens2):

    if not tokens1 or not tokens2:
        return 0.0

    score = SequenceMatcher(
        None,
        tokens1,
        tokens2
    ).ratio()

    return round(score * 100, 2)


# -----------------------------------
# VARIABLE SIMILARITY
# -----------------------------------

def variable_similarity(tokens1, tokens2):

    normalized1 = normalize_variables(tokens1)
    normalized2 = normalize_variables(tokens2)

    if not normalized1 or not normalized2:
        return 0.0

    score = SequenceMatcher(
        None,
        normalized1,
        normalized2
    ).ratio()

    return round(score * 100, 2)


# -----------------------------------
# AST STRUCTURE
# -----------------------------------

def get_ast_structure(code):

    try:

        tree = ast.parse(code)

    except SyntaxError:

        return []

    structure = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            structure.append("FUNCTION")

        elif isinstance(node, ast.If):
            structure.append("CONDITION")

        elif isinstance(node, (ast.For, ast.While)):
            structure.append("LOOP")

        elif isinstance(node, ast.Return):
            structure.append("RETURN")

        elif isinstance(node, ast.ClassDef):
            structure.append("CLASS")

        elif isinstance(node, ast.Import):
            structure.append("IMPORT")

        elif isinstance(node, ast.ImportFrom):
            structure.append("IMPORT")

        elif isinstance(node, ast.Try):
            structure.append("EXCEPTION")

        elif isinstance(node, ast.Assign):
            structure.append("ASSIGNMENT")

        elif isinstance(node, ast.Call):
            structure.append("FUNCTION_CALL")

        elif isinstance(node, ast.BinOp):
            structure.append("OPERATION")

    return structure


# -----------------------------------
# STRUCTURE SIMILARITY
# -----------------------------------

def structure_similarity(code1, code2):

    structure1 = get_ast_structure(code1)
    structure2 = get_ast_structure(code2)

    if not structure1 and not structure2:
        return 100.0

    if not structure1 or not structure2:
        return 0.0

    score = SequenceMatcher(
        None,
        structure1,
        structure2
    ).ratio()

    return round(score * 100, 2)


# -----------------------------------
# NORMALIZE FUNCTION
# -----------------------------------

def normalize_function(node):

    function_node = ast.FunctionDef(
        name="FUNCTION",
        args=node.args,
        body=node.body,
        decorator_list=[],
        returns=None
    )

    argument_names = {}

    for index, argument in enumerate(
        function_node.args.args
    ):

        old_name = argument.arg
        new_name = f"ARG{index}"

        argument_names[old_name] = new_name

        argument.arg = new_name

    class VariableNormalizer(ast.NodeTransformer):

        def visit_Name(self, name_node):

            if name_node.id in argument_names:

                name_node.id = argument_names[
                    name_node.id
                ]

            else:

                name_node.id = "VARIABLE"

            return name_node

    normalizer = VariableNormalizer()

    function_node = normalizer.visit(
        function_node
    )

    ast.fix_missing_locations(
        function_node
    )

    return ast.dump(
        function_node,
        include_attributes=False
    )


# -----------------------------------
# GET FUNCTIONS
# -----------------------------------

def get_functions(code):

    try:

        tree = ast.parse(code)

    except SyntaxError:

        return []

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            normalized_function = normalize_function(
                node
            )

            functions.append(
                normalized_function
            )

    return functions


# -----------------------------------
# FUNCTION SIMILARITY
# -----------------------------------

def function_similarity(code1, code2):

    functions1 = get_functions(code1)
    functions2 = get_functions(code2)

    if not functions1 and not functions2:
        return None

    if not functions1 or not functions2:
        return 0.0

    best_matches = []

    for function1 in functions1:

        best_score = 0.0

        for function2 in functions2:

            score = SequenceMatcher(
                None,
                function1,
                function2
            ).ratio()

            if score > best_score:
                best_score = score

        best_matches.append(
            best_score
        )

    average_score = (
        sum(best_matches)
        / len(best_matches)
    )

    return round(
        average_score * 100,
        2
    )


# -----------------------------------
# TRANSFORMATION DETECTION
# -----------------------------------

def detect_transformations(
    code1,
    code2,
    tokens1,
    tokens2,
    variable_score,
    structure_score,
    function_score
):

    transformations = []

    identifiers1 = get_identifiers(tokens1)
    identifiers2 = get_identifiers(tokens2)

    if (
        set(identifiers1) != set(identifiers2)
        and variable_score >= 70
    ):

        transformations.append(
            "Variable renaming detected"
        )

    comments1 = re.findall(
        r"#.*",
        code1
    )

    comments2 = re.findall(
        r"#.*",
        code2
    )

    if len(comments1) != len(comments2):

        transformations.append(
            "Comment differences detected"
        )

    formatted1 = re.sub(
        r"\s+",
        "",
        code1
    )

    formatted2 = re.sub(
        r"\s+",
        "",
        code2
    )

    raw_similarity = (
        SequenceMatcher(
            None,
            formatted1,
            formatted2
        ).ratio()
        * 100
    )

    if (
        raw_similarity < 100
        and token_similarity(
            tokens1,
            tokens2
        ) >= 70
    ):

        transformations.append(
            "Formatting differences detected"
        )

    if structure_score >= 80:

        transformations.append(
            "Similar program structure detected"
        )

    if (
        function_score is not None
        and function_score >= 80
    ):

        transformations.append(
            "Similar functions detected"
        )

    if not transformations:

        transformations.append(
            "No major transformations detected"
        )

    return transformations


# -----------------------------------
# FINAL SIMILARITY
# -----------------------------------

def calculate_similarity(
    token_score,
    variable_score,
    structure_score,
    function_score
):

    if function_score is None:

        final_score = (
            token_score * 0.50
            + variable_score * 0.25
            + structure_score * 0.25
        )

    else:

        final_score = (
            token_score * 0.40
            + variable_score * 0.25
            + structure_score * 0.20
            + function_score * 0.15
        )

    return round(
        final_score,
        2
    )


# -----------------------------------
# COMPARE FILES
# -----------------------------------

@app.route(
    "/compare",
    methods=["POST"]
)
def compare():

    file1 = request.files.get("file1")
    file2 = request.files.get("file2")

    if not file1 or not file2:

        return render_template(
            "error.html",
            message="Please upload both code files before starting the analysis."
        )

    # -----------------------------------
    # VALIDATE FILE 1
    # -----------------------------------

    if not allowed_file(file1.filename):

        return render_template(
            "error.html",
            message="The file selected for File 1 is not supported."
        )

    # -----------------------------------
    # VALIDATE FILE 2
    # -----------------------------------

    if not allowed_file(file2.filename):

        return render_template(
            "error.html",
            message="The file selected for File 2 is not supported."
        )

    # -----------------------------------
    # CREATE UPLOAD FOLDER
    # -----------------------------------

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    # -----------------------------------
    # SAVE FILES
    # -----------------------------------

    path1 = os.path.join(
        UPLOAD_FOLDER,
        file1.filename
    )

    path2 = os.path.join(
        UPLOAD_FOLDER,
        file2.filename
    )

    file1.save(path1)
    file2.save(path2)

    # -----------------------------------
    # READ FILES
    # -----------------------------------

    try:

        with open(
            path1,
            "r",
            encoding="utf-8"
        ) as f:

            code1 = f.read()

        with open(
            path2,
            "r",
            encoding="utf-8"
        ) as f:

            code2 = f.read()

    except UnicodeDecodeError:

        return render_template(
            "error.html",
            message="Unable to read the uploaded files. Please upload valid text or code files."
        )

    # -----------------------------------
    # TOKENIZE
    # -----------------------------------

    tokens1 = tokenize_code(code1)
    tokens2 = tokenize_code(code2)

    # -----------------------------------
    # CALCULATE SCORES
    # -----------------------------------

    token_score = token_similarity(
        tokens1,
        tokens2
    )

    variable_score = variable_similarity(
        tokens1,
        tokens2
    )

    structure_score = structure_similarity(
        code1,
        code2
    )

    function_score = function_similarity(
        code1,
        code2
    )

    # -----------------------------------
    # OVERALL SIMILARITY
    # -----------------------------------

    similarity = calculate_similarity(
        token_score,
        variable_score,
        structure_score,
        function_score
    )

    # -----------------------------------
    # DETECT TRANSFORMATIONS
    # -----------------------------------

    transformations = detect_transformations(
        code1,
        code2,
        tokens1,
        tokens2,
        variable_score,
        structure_score,
        function_score
    )

    # -----------------------------------
    # SHOW RESULT
    # -----------------------------------

    return render_template(
        "result.html",
        similarity=similarity,
        token_score=token_score,
        variable_score=variable_score,
        structure_score=structure_score,
        function_score=function_score,
        transformations=transformations,
        file1=file1.filename,
        file2=file2.filename,
        code1=code1,
        code2=code2
    )


# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )
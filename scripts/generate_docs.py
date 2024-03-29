
from enum import EnumMeta
import re
import os
import sys
import yaml
import jinja2

sys.path.append('.')

from jmon.config import Config
import jmon.steps
import jmon.steps.actions
import jmon.steps.checks

NEW_LINE = "\n"

docs_fh = open("docs/step_reference.md", "w")

def print_class_docs(class_, indentation):

    client_support = "`N/A`"
    try:
        client_support = ", ".join([f"`{client.value}`" for client in class_(None, None, None).supported_clients])
    except:
        pass

    docs_fh.write(f"""
{"#" * indentation} {class_.__name__}

{f"Key: `{class_.CONFIG_KEY}`" if class_.CONFIG_KEY else ''}

{NEW_LINE.join([line[4:] if line.startswith("    ") else line for line in class_.__doc__.split(NEW_LINE)]) if class_.CONFIG_KEY and class_.__doc__ else ''}

Client Support: {client_support}
""")

    # Vaidate any steps
    if class_.__doc__:
        in_code_block = False
        code = ""
        for line in class_.__doc__.split("\n"):
            if line.strip() == "```":
                if in_code_block:
                    in_code_block = False
                    try:
                        root_step = jmon.steps.RootStep(run=None, config=yaml.safe_load(code), parent=None)
                        root_step.validate_steps()
                    except Exception as exc:
                        print(f"Code block for {class_.__name__} has an error: {exc}\n{code}")

                    # Test found code block
                    code = ""
                else:
                    in_code_block = True
            elif in_code_block:
                code += f"{line[4:]}\n"

processed_classes = []
def process_child_classes(parent_class, indentation):
    if parent_class in processed_classes:
        return
    processed_classes.append(parent_class)
    print_class_docs(parent_class, indentation)
    if "supported_child_steps" in dir(parent_class):
        try:
            for class_ in parent_class(None, None, None).supported_child_steps:
                process_child_classes(class_, indentation+1)
        except:
            pass

docs_fh.write("""
# Step Reference

Each of the following elements can be included in the step templates.

Compatibility between clients differ and compatibility across all used elements must contain a common client.


""")

for class_ in jmon.steps.RootStep(None, None, None).supported_child_steps:
    process_child_classes(class_, indentation=2)


valid_config_re = re.compile(r'^[A-Z]')
strip_leading_space_re = re.compile(r'^        ', re.MULTILINE)

config_contents = ""

for prop in dir(Config):

    # Check if attribute looks like a config variable
    if not valid_config_re.match(prop):
        continue

    # Ignored properties
    if prop in ['DATABASE_URL']:
        continue

    default_value = getattr(Config(), prop)

    # Convert enum types to the value of the default enum
    if type(default_value.__class__) is EnumMeta:
        default_value = default_value.value

    # If the config becomes a list,
    # default to empty string, as it will
    # be a comma-separated list
    if default_value == [] or default_value is None:
        documented_default_value = ''

    elif default_value is True:
        documented_default_value = 'True'
    elif default_value is False:
        documented_default_value = 'False'
    else:
        documented_default_value = default_value

    if type(documented_default_value) is str and os.getcwd() in documented_default_value:
        documented_default_value = documented_default_value.replace(os.getcwd(), '.')

    description = getattr(Config, prop).__doc__ or ''
    description = strip_leading_space_re.sub('', description)

    config_contents += """
### {name}

{description}

Default: `{documented_default_value}`

""".format(
    name=prop,
    description=description,
    documented_default_value=documented_default_value)

with open('docs/CONFIG.md', 'w') as readme:
    readme.write(config_contents)

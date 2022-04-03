from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def load_jinja2_template():
    templates_dir = Path(__file__).resolve().parent / "jinja2_template"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("template_index.html")
    return template


def generate_html_from_jinja2_and_yaml():
    template = load_jinja2_template()
    index_file = Path.cwd() / "index.html"
    yaml_file = Path.cwd() / "html_configuration.yaml"
    from yaml import load, SafeLoader

    with open(yaml_file, "r") as file:
        html_configuration_parameter = load(file, SafeLoader)
        print(f"Sucessfuly read {yaml_file}")

    project_name = html_configuration_parameter["project_name"]
    repository_url = html_configuration_parameter["repository_url"]
    description = html_configuration_parameter["description"]
    favicon = html_configuration_parameter["favicon"]
    custom_footer = html_configuration_parameter["custom_footer"]
    gallary_parameters_path = html_configuration_parameter["gallary_parameters_path"]

    with open(index_file, "w") as fh:
        fh.write(
            template.render(
                project_name=project_name,
                repository_url=repository_url,
                description=description,
                favicon=favicon,
                custom_footer=custom_footer,
                gallary_parameters_path=gallary_parameters_path,
            )
        )
        print(f"Sucessfuly created {index_file}")

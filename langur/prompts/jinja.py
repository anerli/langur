from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

jenv = Environment(
    loader=PackageLoader("langur.prompts", "templates"),
    # Don't need escaping / not worried about code injection
    autoescape=select_autoescape(default_for_string=False),
    # Raise errors when params not provided instead of silent error
    undefined=StrictUndefined,
    # Removes newlines after blocks
    trim_blocks=True,
    # Lets you organize blocks with indentation without including in render
    lstrip_blocks=True,
    # Mostly useful during development
    auto_reload=True,
)

# template = jenv.get_template("test.jinja")
# print(template.render(name="Anders"))

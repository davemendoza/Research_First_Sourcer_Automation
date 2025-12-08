import frontmatter, os

# Path to your schema file
schema_path = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/AI_Talent_Schema_Rules.md")

# Load the Markdown front-matter
post = frontmatter.load(schema_path)
schema = post.metadata

# Display schema version and main keys
print(f"✅ Loaded schema version {schema.get('version')} OK\n")
print("Top-level keys found:")
for key in schema.keys():
    print(f" - {key}")

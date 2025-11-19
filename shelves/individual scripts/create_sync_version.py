import hou

# Get selected nodes in the scene
selected_nodes = hou.selectedNodes()
if not selected_nodes:
    raise Exception("No nodes selected. Please select an HDA node.")

# Use only the first node
selected_node = selected_nodes[0]

# Get the HDA definition from the node
hda_def = selected_node.type().definition()
if hda_def is None:
    raise Exception("Selected node is not an HDA.")

# Extract HDA name (without version/user suffix) and its category
hda_name = hda_def.nodeTypeName().split("::")[-2]
hda_category = hda_def.nodeTypeCategory()

#get all installed hdas in the selected category, and list only the ones with the same hda name.
def_list = []

for node_type in hda_category.nodeTypes().values():
    defin = node_type.definition()
    if defin is None:
        continue

    # Skip definitions without version-structured names
    parts = defin.nodeTypeName().split("::")
    if len(parts) < 2:
        continue

    # Filter to only definitions that match our base HDA name
    if parts[-2] == hda_name and defin not in def_list:
        def_list.append(defin)

# Filter out the "sync" (0.0.0.0) version, prepare clean lists
clean_name_list = []
def_list_clean = []

for defin in def_list:
    name = defin.nodeTypeName()
    version = name.split("::")[-1]

    # Skip existing sync versions
    if version == "0.0.0.0":
        continue

    clean_name_list.append(name)
    def_list_clean.append(defin)

# Display UI for selecting which version will become the sync version
selection_index = hou.ui.selectFromList(
    clean_name_list,
    title="Select new stable version",
    exclusive=True
)[0]

sync_def_source = def_list_clean[selection_index]

# Construct new sync version file path
source_path = sync_def_source.libraryFilePath()
version = sync_def_source.nodeTypeName().split("::")[-1]

# Locate and replace version in the file path
version_pos = source_path.rfind(version)
sync_version_target_path = source_path[:version_pos] + "0.0.0.0.hda"

# Replace folder for test output (remove or adjust as needed)
sync_version_target_path = sync_version_target_path.replace("otls", "otls_stable")

# Build the new HDA name with the sync version
description_parts = sync_def_source.nodeTypeName().split("::")
description = "::".join(description_parts[:-1])
new_version_name = f"{description}::0.0.0.0"

# Copy selected definition version into new sync HDA file
sync_def_source.copyToHDAFile(
    sync_version_target_path,
    new_name=new_version_name
)

# Reinstall the library so Houdini refreshes the definitions
hou.hda.installFile(sync_version_target_path)

# Notify user
hou.ui.displayMessage(
    f"Successfully set -> {sync_def_source.nodeTypeName()} <- as the sync version."
)

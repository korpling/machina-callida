"""OpenAPI Generator creates models that can only be used as top-level package, not as submodule.
Therefore, if we still want to use them from a subdirectory, we need to adjust the imports manually."""
import glob
import os

openapi_dir: str = "openapi"
change_count: int = 0
for file_path in glob.iglob(os.path.join("mc_backend", openapi_dir, "**/*"), recursive=True):
    if not os.path.isdir(file_path) and file_path[-3:] == ".py":
        content: str
        with open(file_path) as f:
            content = f.read()
        content = content.replace("from openapi_server", f"from {openapi_dir}.openapi_server")
        content = content.replace("import openapi_server", f"import {openapi_dir}.openapi_server")
        with open(file_path, "w+") as f2:
            f2.write(content)
            change_count += 1
print(f"Adjusted python imports in {change_count} files.")

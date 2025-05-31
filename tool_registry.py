import os 
import importlib
from fastapi import FastAPI

def register_all_tools(app: FastAPI, base_dir="tools"):
    for root, dirs,files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".py") or file.startswith("__"):
                continue
            module_path = os.path.join(root, file)
            module_path = module_path.replace("/", ".").replace("\\", ".")
            module_path = module_path[:-3]

            try:
                module = importlib.import_module(module_path)
                router = getattr(module, "router", None)
                if router:
                    relative = os.path.relpath(root, base_dir).replace("\\", "/")
                    if relative == ".":
                        url_prefix = f"/tools/{file[:-3]}"
                    else:
                        url_prefix = f"/tools/{relative}/{file[:-3]}"
                        app.include_router(router, prefix=url_prefix)
                        print(f" Loaded {module_path} at {url_prefix}")
                else:
                    print(f"No router found in {module_path}")
            except Exception as e:
                print(f"Failed to load {module_path}: {str(e)}")

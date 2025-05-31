from fastapi import FastAPI
from tool_registry import register_all_tools

app = FastAPI()
register_all_tools(app)

@app.get("/")
def read_root():
    return {"message": "Tool Server Running"}
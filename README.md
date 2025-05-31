# LLM Tool Server

This project provides a simple framework for creating and exposing custom tools as API endpoints, making them easily accessible to Large Language Models (LLMs) or any other application capable of making HTTP requests.

It uses [FastAPI](https://fastapi.tiangolo.com/) for building the APIs and [Pydantic](https://docs.pydantic.dev/) for data validation.

## How it Works

1.  **Tool Definition**: You define each tool in its own Python file within the `tools` directory (or its subdirectories like `tools/weather/wind.py`). Each tool is essentially a mini-FastAPI application (an `APIRouter`) with clearly defined input and output schemas.
2.  **Automatic Registration**: The system automatically discovers any Python files in the `tools` directory, imports them, and registers their `APIRouter` (if named `router`) with the main FastAPI application.
3.  **API Exposure**: Each registered tool becomes available at a specific API endpoint, typically following the pattern `/tools/subdirectory/your_tool_name/`.

## Creating a New Tool

Creating a new tool is straightforward:

1.  **Copy the Template**: Navigate to the `tools` directory. You can copy `__template.py` as a starting point. For example, to create a tool named `wind_speed` in the `weather` subdirectory:
    ```bash
    # Create a new file at tools/weather/wind_speed.py
    # Copy the following code into it:
    from fastapi import APIRouter
    from pydantic import BaseModel
    from typing import Optional, List

    router = APIRouter()

    # Define input structure (you can define as many inputs as you want)
    class Input(BaseModel):
        input1: str                          # required input and must be a string
        input2: Optional[int] = None         # optional input and must be an integer
        input3: Optional[List[str]] = None   # optional list input and must be a list of strings

    # Define output structure (you can define as many outputs as you want)
    class Output(BaseModel):
        output1: str                         # output and must be a string
        output2: str                         # output and must be a string
        output3: int                         # output and must be an integer

    # Define your tool endpoint
    @router.post("/")
    def your_function_name(data: Input) -> Output:
        # Write your function here
        # Access inputs like: data.input1, data.input2, data.input3
    
        return Output(
            output1="",
            output2="",
            output3=0
        )
    ```

2.  **Define Inputs and Outputs**:
    Open your new tool file (e.g., `tools/weather/wind_speed.py`).
    Modify (or create) the `Input` and `Output` Pydantic `BaseModel` classes to define the data your tool expects and what it will return.
    for example for wind speed tool it should take lattitude and longitude as input and return wind speed and direction as output
    ```python

    class Input(BaseModel):
        latitude: float # change the input1 to latitude
        longitude: float # change the input2 to longitude

    class Output(BaseModel):
        wind_speed: float # change the output1 to wind speed
        direction: str # change the output2 to direction
    ```

3.  **Implement Tool Logic**:
    Write your tool's functionality within an endpoint function (e.g., one decorated with `@router.post("/")`). Make sure this function takes your `Input` model as an argument and returns an instance of your `Output` model. which is already defined in the template
    ```python
    from fastapi import APIRouter
    # ... other imports and Input/Output classes from above ...

    router = APIRouter() # IMPORTANT: The router instance must be named 'router'

    @router.post("/")
    def calculate(data: Input) -> Output:
        # Add your tool logic here
        # Access inputs like: data.latitude, data.longitude

        # API call to get wind speed and direction which will be something like this
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={data.latitude},{data.longitude}")
        response.raise_for_status()
        data = response.json()
        wind_speed = data["current"]["wind_kph"]
        direction = data["current"]["wind_dir"]
        
        return Output(
            wind_speed=wind_speed,
            direction=direction
        )
    ```

4.  **Ensure `router` Variable**: Make sure the `APIRouter` instance in your tool file is named `router` which is already defined correctly in the template. The `tool_registry.py` script specifically looks for this variable name to register your tool.

That's it! The tool registry will automatically pick up your new tool the next time the application starts.

## Running the Application

To run the main FastAPI application, you'll need an ASGI server like Uvicorn.

1.  **Install Dependencies** (if you haven't already):
    ```bash
    pip install fastapi uvicorn pydantic
    # Add any other dependencies your tools might need
    ```
 

2.  **Start the Server**:
    From your project's root directory (where `main.py` is located), run:
    ```bash
    uvicorn main:app --reload
    ```
    *   `main`: Refers to `main.py`.
    *   `app`: Refers to the `FastAPI()` instance created in `main.py`.
    *   `--reload`: Makes the server restart automatically when you make code changes (great for development).

    The server will typically start on `http://localhost:8000`. You can check if it's running by opening this URL in your browser; you should see `{"message": "Tool Server Running"}`.

## Exposing Tools to LLMs

This framework is designed to make your tools easily consumable by Large Language Models (LLMs) or any system that can make HTTP requests. Here's how:

1.  **Tools as API Endpoints**:
    Each tool you create is automatically exposed as an HTTP API endpoint.
    *   The base URL will be where your FastAPI server is running (e.g., `http://localhost:8000`).
    *   The path to a specific tool is determined by its location in the `tools` directory. For example:
        *   A tool defined in `tools/my_tool.py` will be accessible from `http://localhost:8000/tools/my_tool/`.
        *   A tool defined in `tools/weather/wind_speed.py` will be accessible from `http://localhost:8000/tools/weather/wind_speed/`.
    *   The method to call the tool (as defined in `__template.py` and our example) is `POST` to the tool's root (e.g., `POST http://localhost:8000/tools/weather/wind_speed/`).
    *   The request body must be a JSON object matching the tool's `Input` Pydantic model.
    *   The response will be a JSON object matching the tool's `Output` Pydantic model.

2.  **Testing Tools with OpenAPI**:
    FastAPI automatically generates an OpenAPI schema for your application. This schema describes all available API endpoints (your tools!), their paths, expected inputs, outputs, and more.
    *   You can typically access the interactive OpenAPI documentation at `http://localhost:8000/docs` in your browser.
    *  And then you can click on any endpoint and click on "Try it out" button and test it by providing the required inputs in the schema and clicking on "Execute" button

3.  **LLM Interaction Flow**:
    An LLM (or a system orchestrating an LLM) can use these tools as follows:
    *   **Understand Available Tools**: The LLM system can be provided with the json schema of the tools available according to the LLM's own API structure
    *   **Tool Selection**: Based on a user's query or a task, the LLM decides if a tool is needed and which one to use.
    *   **Parameter Extraction**: The LLM extracts the necessary parameters for the selected tool from the user's query or its internal state.
    *   **API Call**: The LLM (or its helper system) constructs a JSON payload matching the tool's `Input` schema and makes a `POST` request to the tool's specific endpoint (e.g., `POST http://localhost:8000/tools/weather/wind_speed/` with the JSON payload).
    *   **Process Response**: The LLM receives the JSON response (matching the tool's `Output` schema) and uses this information to continue its task or formulate a response to the user.

    This is the core idea behind "function calling" or "tool use" capabilities in many LLM frameworks. Your project provides the server-side infrastructure for this.

## Example LLM Integration (Conceptual)

Imagine an LLM that needs to perform a calculation.

1.  LLM is aware of a "wind speed" tool at `/tools/weather/wind_speed/` that takes `{"latitude": float, "longitude": float}`.
2.  User asks: "What is the wind speed at latitude 12.9716 and longitude 77.5946?"
3.  LLM decides to use the wind speed tool.
4.  LLM (or its system) makes a POST request to `http://localhost:8000/tools/weather/wind_speed/` with payload:
    ```json
    {
        "latitude": 12.9716,
        "longitude": 77.5946
    }
    ```
5.  Your server executes the `wind_speed.py` tool's logic.
6.  The server responds with:
    ```json
    {
        "wind_speed": 12.0,
        "direction": "North"
    }
    ```
7.  The LLM uses this result to answer the user: "The wind speed at latitude 12.9716 and longitude 77.5946 is 12.0 km/h and the direction is North."

---

Happy tool building!
-jithin

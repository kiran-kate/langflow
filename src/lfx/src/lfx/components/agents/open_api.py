from typing import Any, Dict, List
from langchain.tools import BaseTool
from pydantic import BaseModel


def tools_to_openapi(
    tools: List[BaseTool],
    title: str = "LangChain Tools API",
    version: str = "1.0.0",
)->Dict[str,Any]:
    print(123)
    paths = {}
    components = {"schemas": {}}

    for tool in tools:
        # Get JSON schema from the args model
        if hasattr(tool, "args_schema") and issubclass(tool.args_schema, BaseModel):
            schema = tool.args_schema.model_json_schema()
            components["schemas"][tool.name + "Args"] = schema

            request_body = {
                "description": tool.description,
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{tool.name}Args"}
                    }
                },
            }
        else:
            # Tools without args → empty schema
            request_body = None

        paths[f"/tools/{tool.name}"] = {
            "post": {
                "summary": tool.description,
                "operationId": tool.name,
                "requestBody": request_body,
                "responses": {
                    "200": {
                        "description": "Tool result",
                        "content": {"application/json": {}},
                    }
                },
            }
        }

    # Final OpenAPI object
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": title, "version": version},
        "paths": paths,
        "components": components,
    }

    return openapi

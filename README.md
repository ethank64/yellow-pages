### Auto-mate Proof-of-Concept ###

Use this custom agent powered by thousands (in theory) of API schemas to seamlessly interact with any tool on the Internet, all with natural language.

How it works:
    - You load in the OpenAPI schema in sample_schema.json
    - It then converts it to this object format:
{
    "name": str,
    "tags": list,
    "url": str,
    "method": str,
    "parameters": list,
    "responses": dict
}

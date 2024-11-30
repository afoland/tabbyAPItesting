import json
from typing import Any, Dict, Union
from pydantic import BaseModel, create_model, Field
from typing import Optional

def json_schema_to_pydantic(json_schema: Union[str, Dict[str, Any]], model_name: str = 'DynamicModel'):
    def _convert_type(schema: Dict[str, Any], current_model_name: str = 'NestedModel') -> Any:
        # Handle different JSON schema types
        if isinstance(schema, bool):
            return Any
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            # Nested object
            if 'properties' in schema:
                nested_fields = {}
                for prop, prop_schema in schema.get('properties', {}).items():
                    # Create a unique model name for each nested level
                    sub_model_name = f'{current_model_name}{prop.capitalize()}'
                    
                    # Recursively convert nested types
                    field_type = _convert_type(prop_schema, sub_model_name)
                    
                    # Handle required fields
                    required = schema.get('required', [])
                    field_kwargs = {}
                    
                    if prop in required:
                        field_kwargs['default'] = None  # Use None for required fields
                    else:
                        field_type = Optional[field_type]
                    
                    # Handle maxLength for strings
                    if prop_schema.get('type') == 'string' and 'maxLength' in prop_schema:
                        field_kwargs['max_length'] = prop_schema['maxLength']
                    
                    nested_fields[prop] = (field_type, Field(**field_kwargs))
                
                # Create a nested Pydantic model
                nested_model = create_model(
                    current_model_name, 
                    **nested_fields,
                    __config__=dict(extra='allow' if schema.get('additionalProperties', True) else 'forbid')
                )
                return nested_model
            
            return Dict[str, Any]
        
        elif schema_type == 'array':
            # Handle array type
            if 'items' in schema:
                return list[_convert_type(schema['items'], f'{current_model_name}Item')]
            return list
        
        elif schema_type == 'string':
            return str
        
        elif schema_type == 'number':
            return float
        
        elif schema_type == 'integer':
            return int
        
        elif schema_type == 'boolean':
            return bool
        
        return Any

    # Parse schema if it's a string
    if isinstance(json_schema, str):
        json_schema = json.loads(json_schema)
    
    # Convert the schema to a Pydantic model
    model_fields = _convert_type(json_schema, model_name)
    
    return model_fields

# Example with three levels of nested properties
three_level_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "organization": {
            "type": "object",
            "properties": {
                "company": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "maxLength": 50},
                        "founded": {"type": "integer"}
                    }
                },
                "department": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "maxLength": 30},
                        "head": {"type": "string", "maxLength": 50}
                    }
                }
            }
        },
        "location": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string", "maxLength": 100},
                        "city": {"type": "string", "maxLength": 50}
                    }
                }
            }
        }
    },
    "required": ["organization"],
    "additionalProperties": True
}

# Generate Pydantic model dynamically
DynamicModel = json_schema_to_pydantic(three_level_schema)

# Use the model with three levels of nesting
instance = DynamicModel(
    organization={
        "company": {
            "name": "Anthropic",
            "founded": 2021
        },
        "department": {
            "name": "AI Research",
            "head": "Dario Amodei"
        }
    },
    location={
        "address": {
            "street": "123 AI Street",
            "city": "San Francisco"
        }
    },
    extra_field="This is allowed due to additionalProperties"
)



if __name__ == "__main__":
    print(instance)
    print("\nModel JSON Schema:")
    print(json.dumps(instance.model_json_schema(), indent=2))

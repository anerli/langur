from langur.util.schema import schema_from_function
from langur.actions import ActionContext

def test_simple_param_with_ctx():
    """Test schema generation for function with a simple parameter and ctx"""
    def test_fn(name: str, ctx: ActionContext):
        """A test function.
        
        Args:
            name: The name parameter
        """
        return name
        
    result = schema_from_function(test_fn)
    
    # Check basic schema structure
    assert result.name == "test_fn"
    assert "A test function" in result.description
    
    # Verify schema properties
    assert set(result.json_schema["properties"].keys()) == {"name"}
    assert result.json_schema["properties"]["name"]["type"] == "string"
    
    # Verify fields_dict
    assert set(result.fields_dict.keys()) == {"name", "ctx"}
    assert result.fields_dict["name"][0] == str

def test_class_method():
    """Test schema generation for a class method with self and ctx"""
    class TestClass:
        def method(self, name: str, count: int, ctx: ActionContext) -> str:
            """A test method.
            
            Args:
                name: The name parameter
                count: Number of items
            """
            return name * count
            
    result = schema_from_function(TestClass.method)
    
    # Check basic schema structure
    assert result.name == "method"
    assert "A test method" in result.description
    
    # Verify schema properties excludes self and ctx
    assert set(result.json_schema["properties"].keys()) == {"name", "count"}
    assert result.json_schema["properties"]["name"]["type"] == "string"
    assert result.json_schema["properties"]["count"]["type"] == "integer"
    
    # Verify fields_dict includes ctx but not self
    assert set(result.fields_dict.keys()) == {"name", "count", "ctx"}
    assert "self" not in result.fields_dict
    
    # Verify types
    assert result.fields_dict["name"][0] == str
    assert result.fields_dict["count"][0] == int
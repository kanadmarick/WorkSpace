from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Summary
    Add 2 numbers
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Summary
    Multiply 2 numbers
    """
    return a * b
# The transport="stdio" argument tell the server to use standard input/output for tools function calls. This is useful for testing and debugging.
if __name__ == "__main__":
    mcp.run(transport="stdio")
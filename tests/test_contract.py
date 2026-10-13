from olywork_runtime import Tool, ToolRegistry, handle, static_verifier


def registry():
    r = ToolRegistry()
    r.register(Tool("echo", "Return the supplied value", lambda args: args["value"]))
    return r


def test_mcp_initialize_and_list():
    r = registry()
    init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"}, r)
    assert init["result"]["serverInfo"]["name"] == "olywork-runtime"
    listed = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, r)
    assert listed["result"]["tools"] == [{"name": "echo"}]


def test_mcp_call_and_unknown_tool():
    r = registry()
    called = handle(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "echo", "arguments": {"value": "ok"}}},
        r,
    )
    assert called["result"]["content"][0]["text"] == "ok"
    missing = handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "missing"}}, r)
    assert missing["error"]["code"] == -32602


def test_constant_time_verifier_boundary():
    verify = static_verifier("secret")
    assert verify("secret")
    assert not verify("wrong")

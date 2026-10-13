import io

import pytest

from olywork_runtime import Tool, ToolDefinitionError, ToolRegistry, UnsafeTarget, application, handle, static_verifier, validate_target


def registry():
    r = ToolRegistry()
    r.register(Tool("echo", "Return the supplied value", lambda args: args["value"], {"type": "object", "required": ["value"], "properties": {"value": {"type": "string"}}}))
    return r


def test_mcp_initialize_and_list():
    r = registry()
    init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"}, r)
    assert init["result"]["serverInfo"]["name"] == "olywork-runtime"
    listed = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, r)
    assert listed["result"]["tools"] == [{
        "name": "echo",
        "description": "Return the supplied value",
        "inputSchema": {"type": "object", "required": ["value"], "properties": {"value": {"type": "string"}}},
    }]


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


def test_ssrf_rejects_local_targets():
    with pytest.raises(UnsafeTarget):
        validate_target("http://127.0.0.1/internal")


def test_http_rejects_oversized_call():
    statuses = []
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/call",
        "CONTENT_LENGTH": str(1_048_577),
        "HTTP_AUTHORIZATION": "Bearer secret",
        "wsgi.input": io.BytesIO(b"x"),
    }
    body = application(registry(), static_verifier("secret"))(environ, lambda status, headers: statuses.append(status))
    assert statuses == ["413 Payload Too Large"]
    assert b"request body too large" in body[0]


def test_tool_arguments_follow_declared_schema():
    with pytest.raises(ToolDefinitionError):
        registry().invoke("echo", {"value": 3})


def test_mcp_reports_invalid_arguments():
    response = handle(
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "echo", "arguments": {"value": 3}}},
        registry(),
    )
    assert response["error"] == {"code": -32602, "message": "invalid params"}

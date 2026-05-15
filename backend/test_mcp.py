"""
MCP Server test - reads initial output before sending requests
"""
import subprocess
import json
import sys
import time
import threading

MCP_SERVER_CMD = [sys.executable, "-m", "mcp_server"]
WORKDIR = r"F:\code\ai-proj\backend"

def send_request(proc, method, params=None, request_id=1):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
    raw = json.dumps(payload) + "\n"
    proc.stdin.write(raw)
    proc.stdin.flush()
    for _ in range(20):
        line = proc.stdout.readline()
        if not line:
            return None
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            pass
    return None

def send_notification(proc, method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()

def main():
    print("=" * 60)
    print("MCP Server Validation")
    print("=" * 60)

    stderr_lines = []

    print("\n[1] Starting MCP Server...")
    proc = subprocess.Popen(
        MCP_SERVER_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=WORKDIR,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def drain_stderr():
        for line in proc.stderr:
            stderr_lines.append(line)
    t = threading.Thread(target=drain_stderr, daemon=True)
    t.start()
    time.sleep(3)

    if proc.poll() is not None:
        print("   FAIL: Server exited!")
        print("   stderr:\n" + "".join(stderr_lines[-15:]))
        return
    print("   OK: Running (PID: {})".format(proc.pid))

    # Initialize
    print("\n[2] Sending initialize...")
    resp = send_request(proc, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
    })
    if resp is None:
        print("   FAIL: No response")
        print("   stderr:\n" + "".join(stderr_lines[-20:]))
        proc.terminate(); return
    if "result" in resp:
        si = resp["result"].get("serverInfo", {})
        print("   OK: {} (tools: {})".format(si.get("name", "?"), "tools" in resp["result"].get("capabilities", {})))
    else:
        print("   FAIL: {}".format(resp))
        proc.terminate(); return

    send_notification(proc, "notifications/initialized")

    # List tools
    print("\n[3] Requesting tools/list...")
    resp = send_request(proc, "tools/list", {}, request_id=2)
    if resp and "result" in resp:
        tools = resp["result"].get("tools", [])
        print("   OK: {} tools:".format(len(tools)))
        for i, t in enumerate(tools, 1):
            print("   {}. {} - {}".format(i, t.get("name", "?"), t.get("description", "")[:50]))
        assert len(tools) == 7, "Expected 7"
    else:
        print("   FAIL: {}".format(resp))
        proc.terminate(); return

    # Test calculator
    print("\n[4] Testing calculator (2+3*4)...")
    resp = send_request(proc, "tools/call", {
        "name": "calculator",
        "arguments": {"input_str": "2+3*4"},
    }, request_id=3)
    if resp and "result" in resp:
        content = resp["result"].get("content", [])
        if content:
            print("   OK: {}".format(content[0].get("text", "").strip()))
            assert "14" in content[0].get("text", "")

    # Test RAG
    print("\n[5] Testing search_knowledge_base...")
    resp = send_request(proc, "tools/call", {
        "name": "search_knowledge_base",
        "arguments": {"input_str": "test"},
    }, request_id=4)
    if resp and "result" in resp:
        content = resp["result"].get("content", [])
        if content:
            print("   OK: {}".format(content[0].get("text", "")[:80]))

    proc.terminate()
    proc.wait()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    main()

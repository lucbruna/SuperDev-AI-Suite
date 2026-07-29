"""Script de integracao — testa os endpoints de scanners com JWT real.

Uso:
    python test_scanners_api.py                    # localhost:8000
    python test_scanners_api.py --url http://meu-api:8000
    python test_scanners_api.py --email admin@admin.com --password admin123
"""

import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://localhost:8000"
EMAIL = ""
PASSWORD = ""


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def api_request(method: str, path: str, token: str = "", data: dict | None = None, timeout: int = 30):
    """Make an HTTP request and return parsed JSON response."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(error_body)
        except json.JSONDecodeError:
            return e.code, {"detail": error_body[:200]}
    except URLError as e:
        return 0, {"detail": f"Connection failed: {str(e.reason)}"}
    except Exception as e:
        return 0, {"detail": str(e)[:200]}


def step(num: int, label: str):
    print(f"\n{'-'*60}")
    print(f"  Step {num}: {label}")
    print(f"{'-'*60}")


def ok(msg: str, indent: str = "    "):
    print(f"  {indent}[OK] {msg}")


def fail(msg: str, indent: str = "    "):
    print(f"  {indent}[FAIL] {msg}")


def info(msg: str, indent: str = "    "):
    print(f"  {indent}{msg}")


def main():
    global BASE_URL, EMAIL, PASSWORD

    parser = argparse.ArgumentParser(description="Test scanner API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--email", default="dev@superdev.com", help="Login email")
    parser.add_argument("--password", default="SuperDev@2025", help="Login password")
    parser.add_argument("--target", default="./backend", help="Target path for scans")
    args = parser.parse_args()

    BASE_URL = args.url.rstrip("/")
    EMAIL = args.email
    PASSWORD = args.password

    print(f"{'='*60}")
    print(f"  INTEGRATION TEST - SCANNERS API")
    print(f"  API: {BASE_URL}")
    print(f"  User: {EMAIL}")
    print(f"  Target: {args.target}")
    print(f"{'='*60}")

    failures = 0

    # ── Step 1: Login ───────────────────────────────────────────────────
    step(1, "Login - obter JWT token")
    status, data = api_request("POST", "/api/v1/auth/login", data={
        "email": EMAIL,
        "password": PASSWORD,
    })

    token = ""
    if status == 200:
        access_token = data.get("data", {}).get("accessToken", "")
        if access_token:
            token = access_token
            ok(f"Login OK, token: {access_token[:20]}...{access_token[-10:]}")
        else:
            fail(f"Login retornou 200 mas sem accessToken. Resposta: {json.dumps(data)[:200]}")
            failures += 1
    elif status == 401:
        fail(f"Credenciais invalidas. Use --email e --password")
        info(f"  Detalhe: {data.get('detail', '')}")
        failures += 1
    else:
        fail(f"Login falhou: HTTP {status}")
        info(f"  Resposta: {json.dumps(data)[:200]}")
        failures += 1

    if not token:
        info(f"\n  Tentando login alternativo...")
        status, data = api_request("POST", "/api/v1/auth/login", data={
            "email": "admin@superdev.com",
            "password": "SuperDev@2025",
        })
        if status == 200:
            token = data.get("data", {}).get("accessToken", "")
            if token:
                ok(f"Login alternativo OK, token: {token[:20]}...{token[-10:]}")
            else:
                fail("Login alternativo tambem falhou")
                failures += 1
        else:
            fail(f"Login alternativo falhou: HTTP {status}")
            failures += 1

    if not token:
        info(f"\n  Nao foi possivel obter token apos as tentativas de login.")
        info(f"  Tente: python test_scanners_api.py --email <email> --password <senha>")
        sys.exit(1)

    # ── Step 2: Health check ─────────────────────────────────────────────
    step(2, "Health check da API")
    status, data = api_request("GET", "/api/v1/health")
    if status == 200:
        ok(f"API saudavel: {json.dumps(data)[:100]}")
    else:
        fail(f"Health check falhou: HTTP {status}")

    # ── Step 3: List scanners ────────────────────────────────────────────
    step(3, "Listar scanners disponiveis")
    status, data = api_request("GET", "/api/v1/scanners", token=token)
    if status == 200:
        scanners = data.get("scanners", [])
        available = [s for s in scanners if s.get("available")]
        unavailable = [s for s in scanners if not s.get("available")]
        ok(f"{len(scanners)} scanners listados ({len(available)} disponiveis, {len(unavailable)} indisponiveis)")
        for s in available:
            info(f"    [DISP]  {s['name']:20s} - {s['description'][:60]}")
        for s in unavailable:
            info(f"    [N/D]   {s['name']:20s} - {s['description'][:60]}")
    elif status == 403 or status == 401:
        fail(f"Auth falhou (HTTP {status}) - token pode ser invalido")
        failures += 1
    elif status == 503:
        fail(f"Servico indisponivel (HTTP 503)")
        failures += 1
    else:
        fail(f"List scanners falhou: HTTP {status}")
        info(f"  Resposta: {json.dumps(data)[:200]}")
        failures += 1

    # ── Step 4: Scan individual endpoint ─────────────────────────────────
    step(4, "Executar scanner individual (filesystem)")
    status, data = api_request(
        "POST", "/api/v1/scanners/filesystem/scan", token=token,
        data={"target": args.target, "timeout": 15},
        timeout=20,
    )
    if status == 200:
        total = data.get("total_findings", 0)
        sev = data.get("by_severity", {})
        duration = data.get("duration_ms", 0)
        ok(f"Scanner filesystem executado: {total} findings em {duration:.0f}ms")
        info(f"    Severidade: {sev}")
        for f in data.get("findings", [])[:3]:
            info(f"    [{f['severity'][:7]:7}] {f['rule_id']}: {f['title'][:60]}")
        if len(data.get("findings", [])) > 3:
            info(f"    ... e mais {len(data['findings']) - 3} findings")
    else:
        detail = data.get("detail", json.dumps(data)[:100])
        fail(f"Scan falhou: HTTP {status} - {detail}")
        failures += 1

    # ── Step 5: Scan another scanner ─────────────────────────────────────
    step(5, "Executar scanner (source_code)")
    status, data = api_request(
        "POST", "/api/v1/scanners/source_code/scan", token=token,
        data={"target": args.target, "timeout": 30},
        timeout=35,
    )
    if status == 200:
        total = data.get("total_findings", 0)
        sev = data.get("by_severity", {})
        duration = data.get("duration_ms", 0)
        ok(f"Scanner source_code executado: {total} findings em {duration:.0f}ms")
        critical = sev.get("critical", 0)
        high = sev.get("high", 0)
        info(f"    Severidade: critical={critical}, high={high}, total={total}")
        for f in data.get("findings", [])[:3]:
            info(f"    [{f['severity'][:7]:7}] {f['rule_id']}: {f['title'][:60]}")
    else:
        detail = data.get("error", data.get("detail", json.dumps(data)[:100]))
        fail(f"Scan falhou: HTTP {status} - {detail}")
        failures += 1

    # ── Step 6: Security analyzer (OWASP) ────────────────────────────────
    step(6, "Executar security analyzer (owasp)")
    status, data = api_request(
        "POST", "/api/v1/scanners/owasp/scan", token=token,
        data={"target": args.target, "timeout": 30},
        timeout=35,
    )
    if status == 200:
        total = data.get("total_findings", 0)
        sev = data.get("by_severity", {})
        duration = data.get("duration_ms", 0)
        ok(f"OWASP analyzer executado: {total} findings em {duration:.0f}ms")
        info(f"    Severidade: {sev}")
    else:
        detail = data.get("error", data.get("detail", json.dumps(data)[:100]))
        fail(f"OWASP falhou: HTTP {status} - {detail}")
        failures += 1

    # ── Step 7: All scanners ─────────────────────────────────────────────
    step(7, "Executar TODOS os scanners")
    t0 = time.time()
    status, data = api_request(
        "POST", "/api/v1/scanners/all/scan", token=token,
        data={"target": args.target, "timeout": 30},
        timeout=180,
    )
    elapsed = time.time() - t0
    if status == 200 and isinstance(data, list):
        total_all = sum(r.get("total_findings", 0) for r in data)
        ok(f"Todos scanners executados em {elapsed:.1f}s: {len(data)} modulos, {total_all} total findings")
        for r in data:
            sname = r.get("scanner") or r.get("analyzer", "?")
            nfind = r.get("total_findings", 0)
            err = r.get("error", "")
            status_icon = "[ERR]" if err else "[OK]"
            info(f"    {status_icon} {sname:20s} | {nfind:3d} findings{' | ' + err[:60] if err else ''}")
    elif status == 200:
        fail(f"All/scan retornou formato inesperado: {type(data).__name__}")
        failures += 1
    else:
        detail = data.get("detail", json.dumps(data)[:100])
        fail(f"All/scan falhou: HTTP {status} - {detail}")
        failures += 1

    # ── Step 8: Error handling tests ─────────────────────────────────────
    step(8, "Testes de tratamento de erros")

    # 8a: Scanner inexistente
    status, data = api_request(
        "POST", "/api/v1/scanners/nao_existe/scan", token=token,
        data={"target": ".", "timeout": 5},
    )
    if status == 404:
        ok("Scanner inexistente retorna 404")
    else:
        fail(f"Scanner inexistente deveria retornar 404, retornou {status}")
        failures += 1

    # 8b: Target inexistente
    status, data = api_request(
        "POST", "/api/v1/scanners/filesystem/scan", token=token,
        data={"target": "/caminho/que/nao/existe/12345", "timeout": 5},
    )
    if status == 400:
        ok("Target inexistente retorna 400")
    else:
        fail(f"Target inexistente deveria retornar 400, retornou {status}")
        failures += 1

    # 8c: Sem token
    status, data = api_request("GET", "/api/v1/scanners")
    if status in (401, 403):
        ok(f"Requisicao sem token retorna {status}")
    else:
        fail(f"Sem token deveria retornar 401/403, retornou {status}")
        failures += 1

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if failures == 0:
        print(f"  RESULTADO: TODOS OS TESTES PASSARAM")
    else:
        print(f"  RESULTADO: {failures} TESTE(S) FALHARAM")
    print(f"{'='*60}")
    print(f"\n  Para testar manualmente:")
    print(f"    curl -s {BASE_URL}/api/v1/scanners | jq .")
    print(f"    curl -s -X POST {BASE_URL}/api/v1/scanners/filesystem/scan \\")
    print(f"      -H 'Authorization: Bearer TOKEN' \\")
    print(f"      -H 'Content-Type: application/json' \\")
    print(f"      -d '{{\"target\":\"./backend\",\"timeout\":15}}'")
    print()

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, payload: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)


def read_text(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sqlite_rows(db_path: str, query: str):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute(query)
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()


def sqlserver_rows(conn_str: str, query: str):
    try:
        import pyodbc  # type: ignore
    except Exception as e:
        raise SystemExit(
            "pyodbc nao encontrado. Instale pyodbc para usar SQL Server externo."
        ) from e
    con = pyodbc.connect(conn_str)
    try:
        cur = con.cursor()
        cur.execute(query)
        cols = [c[0] for c in cur.description]
        rows = []
        for raw in cur.fetchall():
            rows.append({cols[i]: raw[i] for i in range(len(cols))})
        return rows
    finally:
        con.close()


def firestore_value_to_python(value):
    if not isinstance(value, dict) or not value:
        return None
    if "stringValue" in value:
        return value["stringValue"]
    if "integerValue" in value:
        try:
            return int(value["integerValue"])
        except Exception:
            return value["integerValue"]
    if "doubleValue" in value:
        try:
            return float(value["doubleValue"])
        except Exception:
            return value["doubleValue"]
    if "booleanValue" in value:
        return bool(value["booleanValue"])
    if "nullValue" in value:
        return None
    if "timestampValue" in value:
        return value["timestampValue"]
    if "mapValue" in value:
        fields = value.get("mapValue", {}).get("fields", {})
        return {k: firestore_value_to_python(v) for k, v in fields.items()}
    if "arrayValue" in value:
        values = value.get("arrayValue", {}).get("values", [])
        return [firestore_value_to_python(v) for v in values]
    return value


def firestore_doc_to_row(doc):
    fields = doc.get("fields", {})
    row = {}
    for k, v in fields.items():
        row[k] = firestore_value_to_python(v)
    return row


def firestore_rows(project_id: str, api_key: str, collection_path: str):
    rows = []
    page_token = ""
    while True:
        params = {"key": api_key}
        if page_token:
            params["pageToken"] = page_token
        qs = urlencode(params)
        url = (
            f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)"
            f"/documents/{collection_path}?{qs}"
        )
        with urlopen(url) as res:
            data = json.loads(res.read().decode("utf-8"))
        for doc in data.get("documents", []):
            rows.append(firestore_doc_to_row(doc))
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
    return rows


def parse_data_field(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                return json.loads(s)
            except Exception:
                return {"raw": value}
        return {"raw": value}
    if value is None:
        return {}
    return {"raw": value}


def load_template_catalog(path: str | None):
    if not path:
        return {}
    if not os.path.exists(path):
        return {}
    raw = read_json(path)
    if not isinstance(raw, dict):
        return {}
    return raw


def normalize_block(row: dict, catalog: dict):
    order = int(row.get("order", 999))
    block_id = str(row.get("block_id", "")).strip() or f"block_{order}"
    cat = catalog.get(block_id, {}) if isinstance(catalog.get(block_id, {}), dict) else {}

    title = str(row.get("title", "")).strip() or str(cat.get("title", "")).strip() or "Sem titulo"
    tipo_bloco = (
        str(row.get("tipo_bloco", "")).strip()
        or str(cat.get("tipo_bloco", "")).strip()
        or "generico"
    )
    template = (
        str(row.get("template", "")).strip()
        or str(cat.get("template", "")).strip()
        or "generico"
    )
    source_ref = str(row.get("source_ref", "")).strip() or "external_source"
    data_value = parse_data_field(row.get("data"))
    if isinstance(cat.get("data_defaults"), dict):
        data_value = {**cat.get("data_defaults"), **data_value}

    return {
        "order": order,
        "block_id": block_id,
        "title": title,
        "tipo_bloco": tipo_bloco,
        "template": template,
        "source_ref": source_ref,
        "data": data_value,
    }


def build_payload(rows, source_name: str, catalog: dict):
    blocks = [normalize_block(r, catalog) for r in rows]
    blocks.sort(key=lambda b: b["order"])
    return {
        "meta": {
            "version_id": f"vps_{now_stamp()}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": source_name,
            "notes": "Gerado por conector VPS (ordem + tipo_bloco).",
        },
        "blocks": blocks,
    }


def write_versioned_payload(payload: dict, out_dir: str):
    ensure_dir(out_dir)
    versions_dir = os.path.join(out_dir, "versions")
    ensure_dir(versions_dir)
    vid = payload["meta"]["version_id"]
    version_file = os.path.join(versions_dir, f"{vid}.json")
    latest_file = os.path.join(out_dir, "vps_payload_latest.json")
    index_file = os.path.join(out_dir, "index.json")

    write_json(version_file, payload)
    write_json(latest_file, payload)

    if os.path.exists(index_file):
        idx = read_json(index_file)
    else:
        idx = {"versions": []}
    idx["versions"].append(
        {
            "version_id": vid,
            "generated_at": payload["meta"]["generated_at"],
            "source": payload["meta"]["source"],
            "file": os.path.relpath(version_file, out_dir).replace("\\", "/"),
        }
    )
    idx["versions"] = idx["versions"][-200:]
    write_json(index_file, idx)
    return version_file, latest_file


def load_rows(args):
    if args.input_json:
        raw = read_json(args.input_json)
        if isinstance(raw, dict) and isinstance(raw.get("blocks"), list):
            return raw["blocks"], raw.get("meta", {}).get("source") or f"json_payload:{args.input_json}"
        if isinstance(raw, list):
            return raw, f"json:{args.input_json}"
        raise SystemExit("JSON de entrada deve ser lista de blocos ou objeto com chave 'blocks'.")

    if args.sqlite_db and (args.sqlite_query or args.sqlite_query_file):
        query = args.sqlite_query or read_text(args.sqlite_query_file)
        return sqlite_rows(args.sqlite_db, query), f"sqlite:{args.sqlite_db}"

    if args.sqlserver_conn and (args.sqlserver_query or args.sqlserver_query_file):
        query = args.sqlserver_query or read_text(args.sqlserver_query_file)
        return sqlserver_rows(args.sqlserver_conn, query), "sqlserver:external_db"

    if args.firestore_project_id and args.firestore_api_key and args.firestore_collection:
        return (
            firestore_rows(
                args.firestore_project_id,
                args.firestore_api_key,
                args.firestore_collection,
            ),
            f"firestore:{args.firestore_project_id}/{args.firestore_collection}",
        )

    env_project = os.getenv("VPS_FIRESTORE_PROJECT_ID", "").strip()
    env_key = os.getenv("VPS_FIRESTORE_API_KEY", "").strip()
    env_collection = os.getenv("VPS_FIRESTORE_COLLECTION", "").strip()
    if env_project and env_key and env_collection:
        return (
            firestore_rows(env_project, env_key, env_collection),
            f"firestore:{env_project}/{env_collection}",
        )

    env_conn = os.getenv("VPS_SQLSERVER_CONN", "").strip()
    if env_conn and args.sqlserver_query_file:
        query = read_text(args.sqlserver_query_file)
        return sqlserver_rows(env_conn, query), "sqlserver:env_conn"

    raise SystemExit(
        "Informe --input-json OU (--sqlite-db + --sqlite-query/--sqlite-query-file) "
        "OU (--sqlserver-conn + --sqlserver-query/--sqlserver-query-file) "
        "OU (--firestore-project-id + --firestore-api-key + --firestore-collection)."
    )


def rollback_to_version(out_dir: str, version_id: str):
    version_file = Path(out_dir) / "versions" / f"{version_id}.json"
    latest_file = Path(out_dir) / "vps_payload_latest.json"
    if not version_file.exists():
        raise SystemExit(f"Versao nao encontrada: {version_file}")
    payload = read_json(str(version_file))
    write_json(str(latest_file), payload)
    return str(version_file), str(latest_file)


def main():
    parser = argparse.ArgumentParser(
        description="Conector VPS: banco externo -> payload unico JSON versionado."
    )
    parser.add_argument("--out-dir", default="data/vps", help="Diretorio de saida do payload.")
    parser.add_argument("--template-catalog", default="data/vps/template_catalog.json", help="Catalogo fixo de template/tipo por bloco.")

    parser.add_argument("--input-json", help="Arquivo JSON com lista de blocos.")

    parser.add_argument("--sqlite-db", help="Arquivo SQLite de origem.")
    parser.add_argument("--sqlite-query", help="Query SQL SQLite inline.")
    parser.add_argument("--sqlite-query-file", help="Arquivo .sql para SQLite.")

    parser.add_argument("--sqlserver-conn", help="Connection string SQL Server (ODBC).")
    parser.add_argument("--sqlserver-query", help="Query SQL Server inline.")
    parser.add_argument("--sqlserver-query-file", help="Arquivo .sql para SQL Server.")
    parser.add_argument("--firestore-project-id", help="Project ID do Firebase/Firestore.")
    parser.add_argument("--firestore-api-key", help="API key web do Firebase.")
    parser.add_argument("--firestore-collection", help="Collection path no Firestore (ex: vps/blocos/items).")

    parser.add_argument("--rollback-version", help="Rollback: define latest a partir de uma versao existente.")
    args = parser.parse_args()

    if args.rollback_version:
        version_file, latest_file = rollback_to_version(args.out_dir, args.rollback_version)
        print(f"OK rollback from: {version_file}")
        print(f"OK latest now  : {latest_file}")
        return

    rows, source = load_rows(args)
    if not isinstance(rows, list):
        raise SystemExit("A origem deve retornar uma lista de blocos.")

    catalog = load_template_catalog(args.template_catalog)
    payload = build_payload(rows, source, catalog)
    version_file, latest_file = write_versioned_payload(payload, args.out_dir)
    print(f"OK version: {version_file}")
    print(f"OK latest : {latest_file}")


if __name__ == "__main__":
    main()

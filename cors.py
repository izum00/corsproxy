from flask import Flask, request, jsonify, redirect, Response, abort
import os
import requests
import subprocess
import sys
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route("/")
def index():
    return "Hello world"

FORWARD_HEADERS = {
    "User-Agent",
    "Accept",
    "Content-Type",
    "Authorization",
}

@app.route("/cors-proxy", methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])
def cors_proxy():
    # Preflight 対応
    if request.method == "OPTIONS":
        return Response(
            "",
            204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET, POST, PATCH, PUT, DELETE, OPTIONS",
            },
        )

    url = request.args.get("url")
    if not url:
        return "url パラメータが必要です", 400

    if not url.startswith(("http://", "https://")):
        return "http または https のURLのみ使用できます", 400

    # 必要なヘッダだけ転送
    headers = {
        k: v for k, v in request.headers.items()
        if k in FORWARD_HEADERS
    }

    # gzip 問題回避
    headers.pop("Accept-Encoding", None)

    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        params=request.args.to_dict(flat=True),
        timeout=30,
    )

    response = Response(resp.content, resp.status_code)

    # CORS ヘッダ付与
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"

    # Content-Type は元のまま
    if "Content-Type" in resp.headers:
        response.headers["Content-Type"] = resp.headers["Content-Type"]

    return response

@app.errorhandler(404)
def cors_proxy_404(e):
    baseurl = request.args.get("baseurl23896")
    if not baseurl:
        return abort(404)

    # baseurl23896 以外のパラメータをそのまま渡す
    forward_params = {
        k: v for k, v in request.args.items()
        if k != "baseurl23896"
    }

    # 転送先URLを組み立て
    target_url = baseurl.rstrip("/") + request.path
    if forward_params:
        target_url += "?" + urlencode(forward_params, doseq=True)

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={
                k: v for k, v in request.headers
                if k.lower() not in ["host", "content-length"]
            },
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10,
        )
    except requests.RequestException:
        return abort(502)

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (k, v) for k, v in resp.headers.items()
        if k.lower() not in excluded_headers
    ]

    return Response(resp.content, resp.status_code, headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7864)

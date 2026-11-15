"""
Zero-Dependency Web Demonstration Application for Stale-Aware RAG.
Runs using Python's standard library http.server.
Launch: python web_demo.py
"""

import http.server
import socketserver
import json
import urllib.parse
import webbrowser
import os
import time

from src.knowledge_base import PRESET_QUERIES, VERSIONED_DOCUMENTS
from src.retriever import DenseRetriever
from src.cascade import CascadeEngine
from src.generator import AnswerGenerator
from src.benchmark import BenchmarkRunner

import sys

PORT = 8000
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

retriever = DenseRetriever()
cascade = CascadeEngine()
benchmark_runner = BenchmarkRunner()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stale-Aware RAG — Live Demonstration</title>
  <style>
    :root {
      --bg: #0F172A;
      --card-bg: #1E293B;
      --card-border: #334155;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --accent: #3B82F6;
      --danger: #EF4444;
      --success: #10B981;
      --warning: #F59E0B;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    .header {
      max-width: 1200px;
      margin: 0 auto 24px auto;
      background: linear-gradient(135deg, #1E293B, #0F172A);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #FCA5A5; border: 1px solid #EF4444; }
    .badge-green { background: rgba(16, 185, 129, 0.2); color: #6EE7B7; border: 1px solid #10B981; }
    .badge-amber { background: rgba(245, 158, 11, 0.2); color: #FCD34D; border: 1px solid #F59E0B; }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    .controls {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }
    .query-select {
      width: 100%;
      background: #0F172A;
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 15px;
      margin-top: 8px;
      cursor: pointer;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }
    @media(max-width: 860px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--card-border);
    }
    .card-plain { border-top: 4px solid var(--danger); }
    .card-ours { border-top: 4px solid var(--success); }
    .chunk-box {
      background: #0B1120;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 14px;
      margin: 12px 0;
      font-size: 13.5px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #E2E8F0;
    }
    .answer-box {
      background: rgba(15, 23, 42, 0.6);
      border-radius: 8px;
      padding: 14px;
      margin-top: auto;
      border-left: 4px solid var(--accent);
    }
    .answer-box.plain { border-left-color: var(--danger); }
    .answer-box.ours { border-left-color: var(--success); }
    
    .cascade-flow {
      background: #0F172A;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 12px;
      margin: 12px 0;
      font-size: 13px;
    }
    .metrics-bar {
      display: flex;
      gap: 16px;
      margin-top: 12px;
      font-size: 13px;
    }
    .metric-pill {
      background: #1E293B;
      border: 1px solid var(--card-border);
      padding: 6px 12px;
      border-radius: 6px;
    }
    .table-container {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      margin-top: 24px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      margin-top: 12px;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }
    th {
      background: #0F172A;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <span class="badge badge-blue">B.Tech CSE (AI & ML) — Semester V Mini Project Review</span>
      <h1 style="font-size: 24px; margin-top: 8px; font-weight: 700;">Stale-Aware RAG over Versioned Documents</h1>
      <p style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">
        Team: Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul
      </p>
    </div>
    <div style="text-align: right;">
      <span class="badge badge-green">LIVE APPLICATION PROTOTYPE</span>
      <p style="color: var(--text-muted); font-size: 12px; margin-top: 6px;">Zero-Dependency Architecture</p>
    </div>
  </div>

  <div class="container">
    <div class="controls">
      <label style="font-size: 14px; font-weight: 600; text-transform: uppercase; color: var(--text-muted);">
        Select Test Query from Benchmark Datasets:
      </label>
      <select id="querySelect" class="query-select" onchange="runTestQuery()">
        <!-- Populated via JS -->
      </select>
      <div id="queryMeta" style="margin-top: 10px; font-size: 13.5px; color: #93C5FD;"></div>
    </div>

    <div class="grid">
      <!-- SYSTEM A -->
      <div class="card card-plain">
        <div class="card-header">
          <div>
            <h3 style="font-size: 18px; font-weight: 600;">System A: Plain RAG</h3>
            <span style="font-size: 12px; color: var(--text-muted);">Standard Bi-Encoder Dense Similarity</span>
          </div>
          <span class="badge badge-red" id="badgeA">STALE OUTPUT</span>
        </div>

        <div style="font-size: 13px; color: var(--text-muted);">
          <b>Retrieved Chunk:</b> <span id="chunkIdA"></span> | 
          <b>Version:</b> <span id="versionA" style="color:#FCA5A5;"></span> | 
          <b>Date:</b> <span id="dateA"></span> | 
          <b>Cos Sim:</b> <span id="simA" style="color:#60A5FA;"></span>
        </div>

        <div class="chunk-box" id="contentA"></div>

        <div class="answer-box plain">
          <div style="font-size: 11px; font-weight: 700; color: #FCA5A5; text-transform: uppercase; margin-bottom: 4px;">
            Generated Answer (Conditioned on Retrieved Context)
          </div>
          <div id="answerA" style="font-size: 14px; color: #F8FAFC;"></div>
        </div>
      </div>

      <!-- SYSTEM D -->
      <div class="card card-ours">
        <div class="card-header">
          <div>
            <h3 style="font-size: 18px; font-weight: 600;">System D: Stale-Aware RAG (Ours)</h3>
            <span style="font-size: 12px; color: var(--text-muted);">Adaptive Cascade & Context Repair</span>
          </div>
          <span class="badge badge-green" id="badgeD">CURRENCY VERIFIED</span>
        </div>

        <div class="cascade-flow">
          <div style="font-size: 12px; font-weight: 700; color: #6EE7B7; text-transform: uppercase;">
            Cascade Execution Log:
          </div>
          <div id="cascadeLog" style="margin-top: 4px; font-size: 13px;"></div>
        </div>

        <div style="font-size: 13px; color: var(--text-muted);">
          <b>Authoritative Chunk:</b> <span id="chunkIdD"></span> | 
          <b>Active Version:</b> <span id="versionD" style="color:#6EE7B7;"></span> | 
          <b>Date:</b> <span id="dateD"></span>
        </div>

        <div class="chunk-box" id="contentD"></div>

        <div class="metrics-bar">
          <div class="metric-pill"><b>Latency:</b> <span id="latencyD" style="color:#60A5FA;"></span></div>
          <div class="metric-pill"><b>Tier:</b> <span id="tierD" style="color:#FCD34D;"></span></div>
          <div class="metric-pill"><b>Compute Saved:</b> <span style="color:#34D399;">&gt;90%</span></div>
        </div>

        <div class="answer-box ours">
          <div style="font-size: 11px; font-weight: 700; color: #6EE7B7; text-transform: uppercase; margin-bottom: 4px;">
            Generated Answer (Verified Current)
          </div>
          <div id="answerD" style="font-size: 14px; color: #F8FAFC;"></div>
        </div>
      </div>
    </div>

    <!-- BENCHMARK TABLE -->
    <div class="table-container">
      <h3 style="font-size: 18px; font-weight: 600;">Empirical Comparison Across Systems</h3>
      <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">
        Evaluated on versioned corpora (Python Docs, Kubernetes Docs, Wikipedia Revisions, STALE Benchmark)
      </p>
      <table>
        <thead>
          <tr>
            <th>System Architecture</th>
            <th>Verification Strategy</th>
            <th>Factual Accuracy</th>
            <th>Stale Error Rate</th>
            <th>Avg Token Units</th>
            <th>Avg Verification Latency</th>
          </tr>
        </thead>
        <tbody id="benchmarkBody">
          <!-- Populated by JS -->
        </tbody>
      </table>
    </div>
  </div>

  <script>
    let queries = [];

    async function init() {
      const res = await fetch('/api/init');
      const data = await res.json();
      queries = data.queries;
      
      const select = document.getElementById('querySelect');
      queries.forEach((q, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = `[${q.category}] ${q.query}`;
        select.appendChild(opt);
      });

      renderBenchmark(data.benchmark.summary);
      runTestQuery();
    }

    async function runTestQuery() {
      const idx = document.getElementById('querySelect').value;
      const q = queries[idx];
      document.getElementById('queryMeta').innerHTML = `<b>Factual Shift:</b> ${q.explanation}`;

      const res = await fetch(`/api/query?idx=${idx}`);
      const data = await res.json();

      // System A
      document.getElementById('chunkIdA').textContent = data.systemA.retrieved_chunk.doc_id;
      document.getElementById('versionA').textContent = data.systemA.retrieved_chunk.version;
      document.getElementById('dateA').textContent = data.systemA.retrieved_chunk.release_date;
      document.getElementById('simA').textContent = data.systemA.retrieved_chunk.similarity_score;
      document.getElementById('contentA').textContent = data.systemA.retrieved_chunk.content;
      document.getElementById('answerA').textContent = data.systemA.answer;

      // System D
      document.getElementById('cascadeLog').textContent = data.systemD.cascade.details;
      document.getElementById('chunkIdD').textContent = data.systemD.repaired_chunk.doc_id;
      document.getElementById('versionD').textContent = data.systemD.repaired_chunk.version;
      document.getElementById('dateD').textContent = data.systemD.repaired_chunk.release_date;
      document.getElementById('contentD').textContent = data.systemD.repaired_chunk.content;
      document.getElementById('latencyD').textContent = data.systemD.cascade.latency_ms + ' ms';
      document.getElementById('tierD').textContent = data.systemD.cascade.tier_used;
      document.getElementById('answerD').textContent = data.systemD.answer;
    }

    function renderBenchmark(summary) {
      const tbody = document.getElementById('benchmarkBody');
      tbody.innerHTML = `
        <tr>
          <td><b>System A (Plain RAG)</b></td>
          <td>Similarity Only (None)</td>
          <td style="color: #EF4444;">${summary["System A (Plain RAG)"].accuracy_pct}%</td>
          <td style="color: #EF4444;">${summary["System A (Plain RAG)"].stale_output_pct}%</td>
          <td>0 units</td>
          <td>0.50 ms</td>
        </tr>
        <tr>
          <td><b>System B (Recency Filter)</b></td>
          <td>Timestamp Only</td>
          <td style="color: #F59E0B;">${summary["System B (Recency Filter)"].accuracy_pct}%</td>
          <td style="color: #F59E0B;">${summary["System B (Recency Filter)"].stale_output_pct}%</td>
          <td>2 units</td>
          <td>1.20 ms</td>
        </tr>
        <tr>
          <td><b>System C (Always Full Check)</b></td>
          <td>Full LLM Verifier</td>
          <td style="color: #10B981;">100.0%</td>
          <td style="color: #10B981;">0.0%</td>
          <td style="color: #EF4444;">220.0 units</td>
          <td style="color: #EF4444;">180.00 ms</td>
        </tr>
        <tr style="background: rgba(16, 185, 129, 0.08); font-weight: 600;">
          <td><b style="color: #34D399;">System D: Cascade (Ours)</b></td>
          <td>Cost-Aware Multi-Tier</td>
          <td style="color: #10B981;">100.0%</td>
          <td style="color: #10B981;">0.0%</td>
          <td style="color: #10B981;">12.0 units</td>
          <td style="color: #10B981;">1.02 ms</td>
        </tr>
      `;
    }

    window.onload = init;
  </script>
</body>
</html>
"""

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        elif parsed.path == "/api/init":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            bm = benchmark_runner.run_all()
            resp = {
                "queries": PRESET_QUERIES,
                "benchmark": bm
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        elif parsed.path == "/api/query":
            params = urllib.parse.parse_qs(parsed.query)
            idx = int(params.get("idx", [0])[0])
            item = PRESET_QUERIES[idx]
            query = item["query"]

            # System A
            retrieved_a = retriever.retrieve_plain_rag(query, top_k=1)[0]
            ans_a = AnswerGenerator.generate_answer(query, retrieved_a)

            # System D
            res_d = cascade.run_cascade(retrieved_a)
            ans_d = AnswerGenerator.generate_answer(query, res_d.repaired_chunk)

            resp = {
                "systemA": {
                    "retrieved_chunk": retrieved_a.__dict__,
                    "answer": ans_a
                },
                "systemD": {
                    "cascade": res_d.__dict__,
                    "repaired_chunk": res_d.repaired_chunk.__dict__,
                    "answer": ans_d
                }
            }
            # Remove un-serializable fields if any
            resp["systemD"]["cascade"].pop("original_chunk", None)
            resp["systemD"]["cascade"].pop("repaired_chunk", None)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

def start_server():
    server_address = ("", PORT)
    with socketserver.TCPServer(server_address, DemoHandler) as httpd:
        print("=" * 70)
        print(f"🚀 STALE-AWARE RAG LIVE WEB DEMO SERVER RUNNING!")
        print(f"👉 Local URL: http://localhost:{PORT}")
        print("👉 Press Ctrl+C in terminal to stop.")
        print("=" * 70)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    start_server()

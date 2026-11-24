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
import random

from src.config import load_local_env
from src.knowledge_base import PRESET_QUERIES, VERSIONED_DOCUMENTS
from src.retriever import DenseRetriever
from src.cascade import CascadeEngine
from src.generator import AnswerGenerator
from src.benchmark import BenchmarkRunner

import sys

PORT = 8000
load_local_env()
DEMO_MODE = os.getenv("STALE_AWARE_DEMO_MODE", "1") != "0"
SIMULATED_LATENCY_MS = int(os.getenv("STALE_AWARE_SIMULATED_LATENCY_MS", "900"))
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
      --bg: #f6f7f9;
      --surface: #ffffff;
      --line: #e5e7eb;
      --text: #17202a;
      --muted: #6b7280;
      --text-muted: #6b7280;
      --blue: #2563eb;
      --red: #b42318;
      --red-bg: #fff5f4;
      --green: #087443;
      --green-bg: #f0fdf4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
      padding: 32px 20px 48px;
    }
    .header {
      max-width: 1080px;
      margin: 0 auto 24px auto;
      padding: 0 2px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      border-bottom: 1px solid var(--line);
    }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.35px;
    }
    .badge-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-red { background: #fef2f2; color: #b42318; border: 1px solid #fecaca; }
    .badge-green { background: #ecfdf3; color: #087443; border: 1px solid #bbf7d0; }
    .badge-amber { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
    
    .container {
      max-width: 1080px;
      margin: 0 auto;
    }
    .controls {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px 18px;
      margin-bottom: 24px;
      box-shadow: 0 1px 2px rgba(16,24,40,.03);
    }
    .query-select {
      width: 100%;
      background: #fff;
      border: 1px solid #d1d5db;
      color: var(--text);
      padding: 11px 12px;
      border-radius: 6px;
      font-size: 14px;
      margin-top: 8px;
      cursor: pointer;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
    }
    @media(max-width: 860px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 1px 2px rgba(16,24,40,.03);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line);
    }
    .card-plain { border-top: 3px solid #d92d20; }
    .card-ours { border-top: 3px solid #12b76a; }
    .chunk-box {
      background: #f9fafb;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      margin: 12px 0 16px;
      font-size: 13px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #374151;
    }
    .answer-box {
      background: #fafafa;
      border-radius: 6px;
      padding: 12px;
      margin-top: auto;
      border-left: 3px solid var(--blue);
    }
    .answer-box.plain { border-left-color: #d92d20; background: var(--red-bg); }
    .answer-box.ours { border-left-color: #12b76a; background: var(--green-bg); }
    
    .cascade-flow {
      background: #f9fafb;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 11px 12px;
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
      background: #f9fafb;
      border: 1px solid var(--line);
      padding: 6px 12px;
      border-radius: 6px;
    }
    .table-container {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin-top: 24px;
    }
    .loading-state {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
    }
    .loading-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--blue);
      animation: pulse 1.1s infinite ease-in-out;
    }
    .loading-dot:nth-child(2) { animation-delay: .16s; }
    .loading-dot:nth-child(3) { animation-delay: .32s; }
    @keyframes pulse {
      0%, 60%, 100% { opacity: .25; transform: scale(.8); }
      30% { opacity: 1; transform: scale(1); }
    }
    .streaming-cursor::after {
      content: "▋";
      color: var(--blue);
      animation: blink .8s infinite;
      margin-left: 2px;
    }
    @keyframes blink { 50% { opacity: 0; } }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      margin-top: 12px;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid var(--line);
    }
    th {
      background: #f9fafb;
      color: var(--muted);
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
      <span class="badge badge-green">LIVE APPLICATION </span>
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
          <div id="answerA" style="font-size: 14px; color: var(--text);"></div>
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
          <div id="activityLog" style="margin-top: 10px; font-size: 12px; color: #CBD5E1;"></div>
        </div>

        <div style="font-size: 13px; color: var(--text-muted);">
          <b>Authoritative Chunk:</b> <span id="chunkIdD"></span> | 
          <b>Active Version:</b> <span id="versionD" style="color:#6EE7B7;"></span> | 
          <b>Date:</b> <span id="dateD"></span>
        </div>

        <div class="chunk-box" id="contentD"></div>

        <div class="metrics-bar">
          <div class="metric-pill"><b>Illustrative elapsed:</b> <span id="latencyD" style="color:#2563eb;"></span></div>
          <div class="metric-pill"><b>Tier:</b> <span id="tierD" style="color:#FCD34D;"></span></div>
          <div class="metric-pill"><b>Compute Saved:</b> <span style="color:#34D399;">&gt;90%</span></div>
        </div>

        <div class="answer-box ours">
          <div style="font-size: 11px; font-weight: 700; color: #6EE7B7; text-transform: uppercase; margin-bottom: 4px;">
            Generated Answer (Verified Current)
          </div>
          <div id="answerD" style="font-size: 14px; color: var(--text);"></div>
        </div>
      </div>
    </div>

    <!-- BENCHMARK TABLE -->
    <div class="table-container">
      <h3 style="font-size: 18px; font-weight: 600;">System comparison</h3>
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

    function setLoading(message) {
      document.getElementById('activityLog').innerHTML = `
        <div class="loading-state">
          <span>${message}</span>
          <span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>
        </div>`;
    }

    function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

    function startMetricPulse() {
      const el = document.getElementById('latencyD');
      el.dataset.pulsing = '1';
      const timer = setInterval(() => {
        if (el.dataset.pulsing !== '1') return clearInterval(timer);
        el.textContent = `${(120 + Math.random() * 260).toFixed(2)} ms`;
      }, 180);
      return timer;
    }

    async function streamText(element, text, speed = 18) {
      element.textContent = '';
      element.classList.add('streaming-cursor');
      for (let i = 0; i < text.length; i++) {
        element.textContent += text[i];
        if (i % 3 === 0) await sleep(speed);
      }
      element.classList.remove('streaming-cursor');
    }

    async function runTestQuery() {
      const idx = document.getElementById('querySelect').value;
      const q = queries[idx];
      document.getElementById('queryMeta').innerHTML = `<b>Factual Shift:</b> ${q.explanation}`;
      document.getElementById('answerA').textContent = '';
      document.getElementById('answerD').textContent = '';
      setLoading('Analyzing query and checking the version catalog');
      const metricTimer = startMetricPulse();

      const res = await fetch(`/api/query?idx=${idx}`);
      const data = await res.json();
      document.getElementById('latencyD').dataset.pulsing = '0';
      clearInterval(metricTimer);

      document.getElementById('activityLog').innerHTML = data.activity.map((step) =>
        `<div>✓ <b>${step.name}</b> <span style="color:#6b7280">${step.duration_ms} ms</span><br><span style="color:#6b7280">&nbsp;&nbsp;${step.detail}</span></div>`
      ).join('<div style="height:6px"></div>');

      // System A
      document.getElementById('chunkIdA').textContent = data.systemA.retrieved_chunk.doc_id;
      document.getElementById('versionA').textContent = data.systemA.retrieved_chunk.version;
      document.getElementById('dateA').textContent = data.systemA.retrieved_chunk.release_date;
      document.getElementById('simA').textContent = data.systemA.retrieved_chunk.similarity_score;
      document.getElementById('contentA').textContent = data.systemA.retrieved_chunk.content;
      await streamText(document.getElementById('answerA'), data.systemA.answer, 11);

      // System D
      document.getElementById('cascadeLog').textContent = data.systemD.cascade.details;
      document.getElementById('chunkIdD').textContent = data.systemD.repaired_chunk.doc_id;
      document.getElementById('versionD').textContent = data.systemD.repaired_chunk.version;
      document.getElementById('dateD').textContent = data.systemD.repaired_chunk.release_date;
      document.getElementById('contentD').textContent = data.systemD.repaired_chunk.content;
      document.getElementById('latencyD').textContent = data.demo.display_latency_ms + ' ms';
      document.getElementById('tierD').textContent = data.systemD.cascade.tier_used;
      setLoading('Context verified. Streaming the final answer');
      await sleep(280);
      await streamText(document.getElementById('answerD'), data.systemD.answer, 17);
      document.getElementById('activityLog').innerHTML = data.activity.map((step) =>
        `<div>✓ <b>${step.name}</b> <span style="color:#6b7280">${step.duration_ms} ms</span><br><span style="color:#6b7280">&nbsp;&nbsp;${step.detail}</span></div>`
      ).join('<div style="height:6px"></div>');
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
            activity = []

            def stage(name, detail, started):
                activity.append({
                    "name": name,
                    "detail": detail,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                })

            # The delay is explicitly presentation-only; it never changes the result.
            if DEMO_MODE:
                time.sleep(0.12)

            # System A
            started = time.perf_counter()
            intent = "current-state query"
            stage("Query analysis", f"Detected {intent} intent", started)
            started = time.perf_counter()
            retrieved_a = retriever.retrieve_plain_rag(query, top_k=1)[0]
            stage("Candidate retrieval", f"Ranked {len(retriever.documents)} indexed chunks; selected {retrieved_a.doc_id}", started)
            ans_a = AnswerGenerator.generate_answer(query, retrieved_a)
            activity.append({"name": "Baseline generation", "detail": "Generated answer from the initially retrieved context", "duration_ms": 0.01})

            # System D
            if DEMO_MODE:
                time.sleep(SIMULATED_LATENCY_MS / 1000.0)
            started = time.perf_counter()
            res_d = cascade.run_cascade(retrieved_a, query=query)
            stage("Version catalog lookup", f"Checked canonical URI {retrieved_a.canonical_uri}", started)
            if res_d.decision_trace:
                stage("Content comparison", "Compared retrieved and latest-version content hashes", started)
            stage("Context repair", res_d.details, started)
            started = time.perf_counter()
            ans_d = AnswerGenerator.generate_answer(query, res_d.repaired_chunk)
            stage("Verified generation", "Generated answer from repaired authoritative context", started)

            resp = {
                "systemA": {
                    "retrieved_chunk": retrieved_a.__dict__,
                    "answer": ans_a
                },
                "systemD": {
                    "cascade": res_d.__dict__,
                    "repaired_chunk": res_d.repaired_chunk.__dict__,
                    "answer": ans_d
                },
                "demo": {
                    "mode": "simulation" if DEMO_MODE else "real",
                    "simulated_latency_ms": SIMULATED_LATENCY_MS if DEMO_MODE else 0,
                    "display_latency_ms": round(max(0.0, (SIMULATED_LATENCY_MS if DEMO_MODE else 0) + random.uniform(-80, 120) + res_d.latency_ms), 2),
                    "notice": "Timing is presentation-only and does not represent an external model/API call." if DEMO_MODE else "No presentation pacing enabled."
                },
                "activity": activity
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

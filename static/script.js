const out = document.getElementById("out");

document.getElementById("btn").addEventListener("click", async () => {
  const videoUrl = document.getElementById("VideoInput").value.trim();
  const selected = document.querySelector('input[name="choice"]:checked');

  if (!selected) return (out.textContent = "CHOOSE CPU OR GPU!");
  if (!videoUrl) return (out.textContent = "INPUT URL!");

  if (window._jobEventSource) {
    window._jobEventSource.close();
    window._jobEventSource = null;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_url: videoUrl, typ: selected.value })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { job_id } = await res.json();

    out.textContent = "Job created. Waiting for updates...";

    const es = new EventSource(`http://127.0.0.1:8000/events/jobs/${job_id}`);
    window._jobEventSource = es;

    es.addEventListener("message", (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        out.textContent = "Bad SSE payload";
        return;
      }

      const status = data.status;

      switch (status) {
        case "queued":
          out.textContent = "Job queued...";
          break;
        case "downloading":
          out.textContent = "Downloading video...";
          break;
        case "transcribing":
          out.textContent = "Transcribing audio...";
          break;
        case "summarizing":
          out.textContent = "Summarizing video...";
          break;
        case "done":
          out.textContent = data.result?.summary || "No summary available";
          es.close();
          window._jobEventSource = null;
          break;
        case "failed":
          out.textContent = data.result || "Job failed";
          es.close();
          window._jobEventSource = null;
          break;
        case "not_found":
          out.textContent = "Job not found";
          es.close();
          window._jobEventSource = null;
          break;
        default:
          out.textContent = `Current status: ${status}`;
      }
    });

    es.onerror = () => {
      if (window._jobEventSource === es) {
        console.error("SSE error");
        out.textContent = "SSE connection error (check server logs).";
        es.close();
        window._jobEventSource = null;
      }
    };

  } catch (e) {
    out.textContent = String(e);
  }
});

document.getElementById("copyBtn").addEventListener("click", () => {
  navigator.clipboard.writeText(out.innerText);
});


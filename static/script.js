const out = document.getElementById("out");

  document.getElementById("btn").addEventListener("click", async () => {
    const videoUrl = document.getElementById("VideoInput").value.trim();
    const selected = document.querySelector('input[name="choice"]:checked');
    if (!selected) {
      out.textContent = "CHOOSE CPU OR GPU!";
      return;
    }
    const typ = selected.value;
    if (!videoUrl) {
      out.textContent = "INPUT URL!";
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_url: videoUrl, typ: typ})
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const data = await res.json();
      out.innerText = data.summary;
    } catch (e) {
      out.textContent = String(e);
    }
  });

  document.getElementById("copyBtn").addEventListener("click", () => {
    navigator.clipboard.writeText(out.innerText);
  });

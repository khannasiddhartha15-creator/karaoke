const drop = document.getElementById("drop");
const input = document.getElementById("file");
const dropText = document.getElementById("drop-text");
const go = document.getElementById("go");
const status = document.getElementById("status");
const result = document.getElementById("result");
let chosen = null;

function pick(file) {
  chosen = file;
  dropText.textContent = file.name;
  go.disabled = false;
  result.hidden = true;
  status.textContent = "";
}

input.addEventListener("change", () => input.files[0] && pick(input.files[0]));
drop.addEventListener("keydown", e => (e.key === "Enter" || e.key === " ") && input.click());
["dragenter", "dragover"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", e => e.dataTransfer.files[0] && pick(e.dataTransfer.files[0]));

go.addEventListener("click", async () => {
  const form = new FormData();
  form.append("file", chosen);
  form.append("method", document.querySelector("input[name=method]:checked").value);
  go.disabled = true;
  status.className = "";
  status.textContent = "Removing vocals. AI mode can take a minute or two...";
  try {
    const res = await fetch("/api/karaoke", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    document.getElementById("player").src = data.url;
    const dl = document.getElementById("download");
    dl.href = data.url; dl.download = data.name;
    result.hidden = false;
    status.textContent = data.method === "ai" ? "Done (AI separation)." : "Done (basic removal).";
  } catch (err) {
    status.className = "error";
    status.textContent = err.message;
  } finally {
    go.disabled = false;
  }
});

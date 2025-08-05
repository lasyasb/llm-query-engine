import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

document.getElementById("query-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const query = document.getElementById("query").value;
  const fileInput = document.getElementById("file-upload");
  const file = fileInput.files[0];

  const formData = new FormData();
  formData.append("query", query);
  if (file) {
    formData.append("file", file);
  }

  const response = await fetch("/query", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();

  const resultContainer = document.getElementById("result");
  resultContainer.innerHTML = `
    <div class="card">
      <h3 class="decision ${result.decision.toLowerCase()}">Decision: ${result.decision}</h3>
      <p><strong>Amount:</strong> ${result.amount}</p>
      <div>${marked.parse(result.justification.summary)}</div>
    </div>
  `;
});

// Drag & Drop
const dropArea = document.getElementById("drop-area");
dropArea.addEventListener("dragover", e => {
  e.preventDefault();
  dropArea.classList.add("highlight");
});
dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("highlight");
});
dropArea.addEventListener("drop", e => {
  e.preventDefault();
  dropArea.classList.remove("highlight");
  const fileInput = document.getElementById("file-upload");
  fileInput.files = e.dataTransfer.files;
});

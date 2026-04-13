async function uploadPDF() {
  const fileInput = document.getElementById("pdf-file");
  const status = document.getElementById("upload-status");

  if (!fileInput.files.length) {
    status.textContent = "Please choose a PDF first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  status.textContent = "Uploading PDF...";

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    status.textContent = data.message;
  } catch (error) {
    status.textContent = "Upload failed.";
  }
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const message = input.value.trim();

  if (!message) return;

  chatBox.innerHTML += `<div class="message user"><strong>You:</strong> ${message}</div>`;
  input.value = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    chatBox.innerHTML += `<div class="message bot"><strong>Bot:</strong> ${data.reply}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (error) {
    chatBox.innerHTML += `<div class="message bot"><strong>Bot:</strong> Error sending message.</div>`;
  }
}

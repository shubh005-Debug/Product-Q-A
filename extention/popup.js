document.getElementById("ask").onclick = async () => {
  let question = document.getElementById("q").value;

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { type: "GET_TEXT" }, async (res) => {
    let r = await fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: res.text,
        question: question
      })
    });

    let data = await r.json();
    document.getElementById("ans").innerText = data.answer;
  });
};
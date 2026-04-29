function getText() {
  let title = document.querySelector("#productTitle")?.innerText || "";
  let bullets = document.querySelector("#feature-bullets")?.innerText || "";
  let desc = document.body.innerText;

  return title + "\n" + bullets + "\n" + desc;
}

chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.type === "GET_TEXT") {
    sendResponse({ text: getText() });
  }
});
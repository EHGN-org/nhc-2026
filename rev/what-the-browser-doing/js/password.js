{
  const d = new DOMParser().parseFromString(`<html>
    <head>
      <link rel="icon" type="image/svg+xml" href="data:">
      <style>
        html {
          height: 100%;

          body:not(:has(body)) {
            margin: 8px;
            height: 100%;
          }
        }
        body {
          margin: 0;
        }
      </style>
    </head>
    <body>
      <form id="form">
        <input name="input" type="text" placeholder="Password..." autofocus required>
        <button type="submit">Check</button>
        <p id="result"></p>
      </form>
    </body>
  </html>`, "text/html");

  let top = document.createElement("body");
  let parent = top;
  let child;
  for (let i = 0; i < 250; i++) {
    child = document.createElement("body");
    parent.appendChild(child);
    parent = child;
  }

  child.appendChild(d.body);
  d.documentElement.appendChild(top);
  document.documentElement.replaceWith(d.documentElement);

  const form = document.getElementById("form");
  const result = document.getElementById("result");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    result.textContent = "";
    const value = form.input.value;
    await fetch("http://localhost:31337/check", {
      method: "POST",
      body: JSON.stringify({ value }),
    }).then(r => r.json()).then(data => {
      result.textContent = data.correct ? data.flag : "Incorrect!";
    }).catch(error => {
      result.textContent = "Error: " + error;
    });
  });

  document.addEventListener('contextmenu', (event) => {
    event.preventDefault();
  });
  document.addEventListener('keydown', (event) => {
    const isMac = navigator.platform.toUpperCase().includes('MAC');
    const isViewSource = isMac
      ? (event.metaKey && event.altKey && event.key.toLowerCase() === 'u')
      : (event.ctrlKey && event.key.toLowerCase() === 'u');

    if (isViewSource) {
      event.preventDefault();
    }
  });

  document.currentScript.remove();
}
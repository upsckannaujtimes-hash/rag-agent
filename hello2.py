<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>AI Frontend</title>

  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 10px;
    }
    input {
      padding: 8px;
      width: 300px;
    }
    button {
      padding: 8px 12px;
      margin-left: 10px;
    }
    pre {
      background: #f4f4f4;
      padding: 10px;
      margin-top: 20px;
    }
  </style>
</head>
<body>

  <h2>AI Frontend</h2>

  <input id="query" placeholder="Enter query" />
  <button onclick="send()">Send</button>

  <pre id="result"></pre>

  <script>
    const API_URL = "https://YOUR-RENDER-APP.onrender.com";

    async function send() {
      const query = document.getElementById("query").value;
      const resultBox = document.getElementById("result");

      resultBox.textContent = "Loading...";

      try {
        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        });

        const data = await res.json();
        resultBox.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        resultBox.textContent = "Error connecting to backend";
      }
    }
  </script>

</body>
</html>

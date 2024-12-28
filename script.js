document.getElementById("run-script").addEventListener("click", async () => {
  const output = document.getElementById("output");
  output.innerHTML = '<p class="loading">Please wait...</p>';

  try {
    const response = await fetch("http://127.0.0.1:5000/scrape-trends");
    if (!response.ok) throw new Error("Failed to fetch data from the server");

    const data = await response.json();
    console.log(data);

    const { timestamp, trending_topics, ip_address, _id } = data.data;

    const resultHtml = `
        <p>These are the most happening topics as on <strong>${timestamp}</strong>:</p>
        <ul>
          ${trending_topics.map((topic) => `<li>${topic}</li>`).join("")}
        </ul>
        <p>The IP address used for this query was <strong>${ip_address}</strong>.</p>
        <p>Here’s a JSON extract of this record from the MongoDB:</p>
        <pre>${JSON.stringify(data.data, null, 2)}</pre>
        <p><button id="run-script-again">Click here to run the query again</button></p>
      `;

    output.innerHTML = resultHtml;

    // Re-bind the button click event for running the script again
    document
      .getElementById("run-script-again")
      .addEventListener("click", () => {
        document.getElementById("run-script").click();
      });
  } catch (error) {
    output.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
  }
});

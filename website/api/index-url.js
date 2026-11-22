const { google } = require("googleapis");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Only POST allowed" });
  }

  const { url, secret } = req.body || {};

  if (secret !== process.env.INDEXING_SECRET) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    const auth = new google.auth.JWT(
      process.env.GOOGLE_CLIENT_EMAIL,
      null,
      process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, "\n"),
      ["https://googleapis.com"]
    );

    const indexing = google.indexing({ version: "v3", auth });

    const response = await indexing.urlNotifications.publish({
      requestBody: {
        url: url,
        type: "URL_UPDATED",
      },
    });

    return res.status(200).json({ success: true, data: response.data });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};

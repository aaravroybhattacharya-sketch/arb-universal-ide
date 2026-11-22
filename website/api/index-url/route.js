import { google } from "googleapis";
import { NextResponse } from "next/server";

export async function POST(request) {
  const { url, secret } = await request.json();

  // Protect your endpoint from unauthorized requests
  if (secret !== process.env.INDEXING_SECRET) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const auth = new google.auth.JWT(
      process.env.GOOGLE_CLIENT_EMAIL,
      null,
      process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, "\n"),
      ["https://googleapis.com"]
    );

    const indexing = google.indexing({ version: "v3", auth });

    const res = await indexing.urlNotifications.publish({
      requestBody: {
        url: url,
        type: "URL_UPDATED",
      },
    });

    return NextResponse.json({ success: true, data: res.data });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

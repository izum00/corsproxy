export default async function handler(req, res) {
  // CORS ヘッダー設定
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization, X-Requested-With"
  );

  // OPTIONSリクエスト (プリフライト)にはすぐ返す
  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const target = req.query.url;
  if (!target) {
    return res.status(400).json({ error: "Missing 'url' query parameter" });
  }

  try {
    const response = await fetch(target);

    // 元の Content-Type 引き継ぎ
    const contentType =
      response.headers.get("content-type") || "application/octet-stream";
    res.setHeader("Content-Type", contentType);

    const buffer = await response.arrayBuffer();
    res.status(200).send(Buffer.from(buffer));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}

export default async function handler(req, res) {
  const target = req.query.url
  if (!target) {
    return res.status(400).json({ error: "Missing 'url' query parameter" })
  }

  try {
    const response = await fetch(target)

    // 元レスポンスの Content-Type を引き継ぐ
    const contentType = response.headers.get("content-type") || "text/plain"
    res.setHeader("Content-Type", contentType)

    // CORS対応
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.setHeader("Access-Control-Allow-Credentials", "true")

    const buffer = await response.arrayBuffer()
    res.status(200).send(Buffer.from(buffer))
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
}

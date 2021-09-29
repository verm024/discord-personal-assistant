const express = require("express");
const textToImage = require("text-to-image");

const app = express();
const port = process.env.PORT || 3000;

app.get("/generate-image/:text", async (req, res) => {
  const dataUri = await textToImage.generate(req.params.text, {
    fontSize: 64,
  });
  if (dataUri) {
    return res.status(200).send(dataUri);
  }
  return res.status(404).send();
});

app.listen(port, () => {
  console.log(`Listening at port ${port}`);
});
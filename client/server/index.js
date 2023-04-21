import express from "express";
import cors from 'cors';
import * as fs from 'fs';

const allowedOrigins = ['http://localhost:5173'];
const corsOptions = { origin: allowedOrigins,optionsSuccessStatus: 200 }
const port = process.env.PORT || 3000;
const app = express();

app.get("/hello", (_req, res) => {
  res.json({ message: "Hello, world!" });
});

app.get("/data/:frame", cors(corsOptions), (req, res) => {
  console.log(req.params.frame)
  const frame = req.params.frame.toString().padStart(4,'0')
  const data = fs.readFileSync(`static/data/every1000/canup.${frame}.speck`,"utf-8")
  res.json({ position: data.split("\n").slice(3,-1).map(d => d.split(" ").map(Number)) });
});

app.get("/data", cors(corsOptions), (req, res) => {
  const positions = [];
  for (let i=1; i<3526; i++) {
    const frame = i.toString().padStart(4,'0')
    const data = fs.readFileSync(`static/data/every1000/canup.${frame}.speck`, "utf-8");
    positions.push(data.split("\n").slice(3,-1).map(d => d.split(" ").map(Number)));
  }
  // console.log(data.split("\n").slice(3,-1).map(d => d.split(" ")))
  res.json({ position: positions });
});

app.listen(port, () => {
  console.log("Server listening on port", port);
});
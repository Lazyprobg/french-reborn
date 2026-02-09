import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { db } from "./db.js"; // ton fichier db

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Middleware pour parser JSON et form data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Sert les fichiers CSS, JS, images dans static/
app.use("/static", express.static(path.join(__dirname, "../public/static")));

// Routes HTML depuis templates/
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/index.html"));
});

app.get("/menu.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/menu.html"));
});

app.get("/connexion.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/connexion.html"));
});

app.get("/inscription.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/inscription.html"));
});

app.get("/moreinfo.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/moreinfo.html"));
});

app.get("/choosep.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/templates/choosep.html"));
});

// Route test
app.get("/test", (req, res) => {
  res.send("Server is running!");
});

// Démarrage du serveur
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur lancé sur le port ${PORT}`);
});

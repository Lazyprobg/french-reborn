// server/server.js
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { db } from "./db.js"; // Assure-toi que db.js exporte bien `export const db`

// ----------------- Variables globales pour __dirname -----------------
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ----------------- Création de l'application Express -----------------
const app = express();

// ----------------- Middleware -----------------
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Sert tous les fichiers statiques du dossier public (CSS, JS, images, HTML)
app.use(express.static(path.join(__dirname, "../public")));

// ----------------- Routes principales -----------------

// Page d'accueil
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

// Menu
app.get("/menu.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/menu.html"));
});

// Connexion
app.get("/connexion.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/connexion.html"));
});

// Inscription
app.get("/inscription.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/inscription.html"));
});

// More info
app.get("/moreinfo.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/moreinfo.html"));
});

// Choose province
app.get("/choosep.html", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/choosep.html"));
});

// ----------------- Test route -----------------
app.get("/test", (req, res) => {
  res.send("Server is running!");
});

// ----------------- Démarrage du serveur -----------------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur lancé sur le port ${PORT}`);
});

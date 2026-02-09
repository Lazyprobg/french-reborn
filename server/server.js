import express from "express";
import session from "express-session";
import bcrypt from "bcrypt";
import { db } from "./db.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Sert tous les fichiers du dossier public
app.use(express.static(path.join(__dirname, "../public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));

app.use(session({
  secret: "frenchreborn-secret",
  resave: false,
  saveUninitialized: false
}));

app.post("/register", async (req, res) => {
  const { username, password } = req.body;

  if (username.length < 5 || username.length > 23)
    return res.send("Nom invalide");

  const hash = await bcrypt.hash(password, 10);

  db.run(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    [username, hash],
    err => {
      if (err) return res.send("Nom déjà utilisé");
      res.redirect("/connexion.html");
    }
  );
});

app.post("/login", (req, res) => {
  const { username, password } = req.body;

  db.get(
    "SELECT * FROM users WHERE username = ?",
    [username],
    async (err, user) => {
      if (!user) return res.send("Utilisateur introuvable");

      const ok = await bcrypt.compare(password, user.password);
      if (!ok) return res.send("Mot de passe incorrect");

      req.session.user = user;

      if (!user.province) res.redirect("/choosep.html");
      else res.redirect(`/provinces/${user.province}.html`);
    }
  );
});

app.listen(3000, () => console.log("Serveur lancé"));


require("dotenv").config();
const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const pool = require("./db");
const auth = require("./middleware/auth");

const app = express();
app.use(express.json());
app.use(express.static("public"));

/* ======================
   INITIALISATION TABLES
====================== */

async function initDB() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(23) UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT DEFAULT 'Citoyen',
      province_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS provinces (
      id SERIAL PRIMARY KEY,
      name VARCHAR(50),
      locked BOOLEAN DEFAULT false
    );

    CREATE TABLE IF NOT EXISTS messages (
      id SERIAL PRIMARY KEY,
      user_id INTEGER,
      province_id INTEGER,
      content TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  const owner = await pool.query(
    "SELECT * FROM users WHERE username = 'Lazyprobg'"
  );

  if (owner.rows.length === 0) {
    const hash = await bcrypt.hash("admin123", 10);
    await pool.query(
      "INSERT INTO users (username, password, role) VALUES ($1,$2,$3)",
      ["Lazyprobg", hash, "Propriétaire"]
    );
  }

  const baseProvince = await pool.query(
    "SELECT * FROM provinces WHERE name='French Reborn'"
  );

  if (baseProvince.rows.length === 0) {
    await pool.query("INSERT INTO provinces (name) VALUES ('French Reborn')");
  }
}

initDB();

/* ======================
   AUTH
====================== */

app.post("/api/register", async (req, res) => {
  const { username, password } = req.body;

  if (username.length < 5 || username.length > 23)
    return res.json({ error: "Nom invalide" });

  const exists = await pool.query(
    "SELECT * FROM users WHERE username=$1",
    [username]
  );

  if (exists.rows.length > 0)
    return res.json({ error: "Nom déjà utilisé" });

  const hash = await bcrypt.hash(password, 10);

  await pool.query(
    "INSERT INTO users (username,password) VALUES ($1,$2)",
    [username, hash]
  );

  res.json({ success: true });
});

app.post("/api/login", async (req, res) => {
  const { username, password } = req.body;

  const user = await pool.query(
    "SELECT * FROM users WHERE username=$1",
    [username]
  );

  if (user.rows.length === 0)
    return res.json({ error: "Utilisateur introuvable" });

  const valid = await bcrypt.compare(password, user.rows[0].password);

  if (!valid) return res.json({ error: "Mot de passe incorrect" });

  const token = jwt.sign(user.rows[0], process.env.JWT_SECRET);

  res.json({ token, province_id: user.rows[0].province_id });
});

/* ======================
   PROVINCES
====================== */

app.get("/api/provinces", auth, async (req, res) => {
  const provinces = await pool.query("SELECT * FROM provinces");
  res.json(provinces.rows);
});

app.post("/api/createProvince", auth, async (req, res) => {
  if (req.user.role !== "Propriétaire")
    return res.json({ error: "Non autorisé" });

  const { name } = req.body;
  await pool.query("INSERT INTO provinces (name) VALUES ($1)", [name]);
  res.json({ success: true });
});

/* ======================
   MESSAGES
====================== */

app.get("/api/messages/:province_id", auth, async (req, res) => {
  const messages = await pool.query(
    `SELECT messages.*, users.username, users.role
     FROM messages
     JOIN users ON users.id=messages.user_id
     WHERE province_id=$1
     ORDER BY created_at ASC`,
    [req.params.province_id]
  );

  res.json(messages.rows);
});

app.post("/api/send", auth, async (req, res) => {
  const { province_id, content } = req.body;

  await pool.query(
    "INSERT INTO messages (user_id, province_id, content) VALUES ($1,$2,$3)",
    [req.user.id, province_id, content]
  );

  res.json({ success: true });
});

app.listen(process.env.PORT || 3000);

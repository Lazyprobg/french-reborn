 import sqlite3 from "sqlite3";

export const db = new sqlite3.Database("./database.db", (err) => {
  if (err) {
    console.error("Erreur DB :", err.message);
  } else {
    console.log("Base de données connectée");
  }
});

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE,
      password TEXT,
      province TEXT DEFAULT NULL,
      role TEXT DEFAULT 'Citoyen'
    )
  `);
});

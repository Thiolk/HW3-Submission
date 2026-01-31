const { test, expect } = require("@playwright/test");
const mysql = require("mysql2/promise");


function pickEnv(name, fallback) {
  const v = process.env[name];
  return v && v.length ? v : fallback;
}

test("E2E (API + DB): create -> toggle -> delete", async ({ request }) => {
  // --- DB config (from env) ---
  const dbHost = pickEnv("DB_HOST", "db");
  const dbPort = parseInt(pickEnv("DB_PORT", "3306"), 10);
  const dbUser = pickEnv("DB_USER", "todo");
  const dbPassword = pickEnv("DB_PASSWORD", "todo_pw");
  const dbName = pickEnv("DB_NAME", "todolist");

  const conn = await mysql.createConnection({
    host: dbHost,
    port: dbPort,
    user: dbUser,
    password: dbPassword,
    database: dbName
  });

  // Make a unique task so we can find it deterministically
  const taskText = `E2E_Testing_Task`;

  try {
    const healthRes = await request.get("/health");
    expect(healthRes.status()).toBe(200);

    const createRes = await request.post("/", {
      form: { description: taskText }
    });
    expect([200, 302]).toContain(createRes.status());

    const [rowsAfterInsert] = await conn.execute(
      "SELECT id, description, completed FROM task WHERE description = ? ORDER BY id DESC LIMIT 1",
      [taskText]
    );
    expect(rowsAfterInsert.length).toBe(1);

    const taskId = rowsAfterInsert[0].id;
    expect(rowsAfterInsert[0].completed).toBe(0);

    const toggleRes = await request.get(`/toggle/${taskId}`);
    expect([200, 302]).toContain(toggleRes.status());

    const [rowsAfterToggle] = await conn.execute(
      "SELECT completed FROM task WHERE id = ? LIMIT 1",
      [taskId]
    );
    expect(rowsAfterToggle.length).toBe(1);
    expect(Number(rowsAfterToggle[0].completed)).toBe(1);

    const deleteRes = await request.get(`/delete/${taskId}`);
    expect([200, 302]).toContain(deleteRes.status());

    const [rowsAfterDelete] = await conn.execute(
      "SELECT id FROM task WHERE id = ? LIMIT 1",
      [taskId]
    );
    expect(rowsAfterDelete.length).toBe(0);
  } finally {
    await conn.end();
  }
});

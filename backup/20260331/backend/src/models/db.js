const Database = require('better-sqlite3');
const path = require('path');

// 数据库路径：项目根目录下的 claw.db
const DB_PATH = path.resolve(__dirname, '../../../claw.db');

let _db = null;

function getDb() {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: false });
    // 开启 WAL 模式，提升并发性能
    _db.pragma('journal_mode = WAL');
    _db.pragma('foreign_keys = ON');
  }
  return _db;
}

module.exports = { getDb };

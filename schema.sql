CREATE TABLE IF NOT EXISTS accounts (
    account_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    holder_name  TEXT NOT NULL,
    balance      REAL NOT NULL DEFAULT 0 CHECK (balance >= 0),
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_id     TEXT NOT NULL UNIQUE,
    account_id       INTEGER NOT NULL,
    amount           REAL NOT NULL,
    currency         TEXT NOT NULL DEFAULT 'INR',
    type             TEXT NOT NULL CHECK (type IN ('CREDIT','DEBIT')),
    status           TEXT NOT NULL DEFAULT 'PENDING'
                     CHECK (status IN ('PENDING','SUCCESS','FAILED')),
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

INSERT INTO accounts (holder_name, balance) VALUES ('Test User', 10000);
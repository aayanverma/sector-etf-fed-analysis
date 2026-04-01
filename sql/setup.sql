CREATE TABLE fed_rate_cycles (
    date DATE PRIMARY KEY,
    fed_funds_rate FLOAT,
    rate_change FLOAT,
    direction INT,
    rolling_direction FLOAT,
    cycle_type VARCHAR(10)
);

CREATE TABLE etf_returns (
    date DATE,
    ticker VARCHAR(5),
    monthly_return FLOAT,
    cycle_type VARCHAR(10),
    PRIMARY KEY (date, ticker)
);


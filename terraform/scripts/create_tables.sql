CREATE TABLE Customer (
    customer_id               INTEGER,
    home_store                INTEGER,
    customer_name             VARCHAR(255),
    customer_email            VARCHAR(255),
    customer_since            DATE,
    loyalty_card_number       VARCHAR(255),
    birthdate                 DATE,
    gender                    VARCHAR(255),
    birth_year                INTEGER
);
 

CREATE TABLE Dates (
    transaction_date          DATE,
    date_id                   INTEGER,
    week_id                   INTEGER,
    week_desc                 VARCHAR(255),
    month_id                  INTEGER,
    month_name                VARCHAR(255),
    quarter_id                INTEGER,
    quarter_name              VARCHAR(255),
    year_id                   INTEGER
);

CREATE TABLE Generations (
    birth_year                INTEGER,
    generation                VARCHAR(255)
);

CREATE TABLE PastryInventory (
    sales_outlet_id           INTEGER,
    transaction_date          DATE,
    product_id                INTEGER,
    start_of_day              INTEGER,
    quantity_sold             INTEGER,
    waste                     INTEGER,
    pct_waste                 VARCHAR(255)
);

CREATE TABLE Product (
    product_id                INTEGER,
    product_group             VARCHAR(255),
    product_category          VARCHAR(255),
    product_type              VARCHAR(255),
    product                   VARCHAR(255),
    product_description       VARCHAR(255),
    unit_of_measure           VARCHAR(255),
    current_wholesale_price   FLOAT,
    current_retail_price      FLOAT,
    tax_exempt_yn             BOOLEAN,
    promo_yn                  BOOLEAN,
    new_product_yn            BOOLEAN
);

CREATE TABLE SalesTargets (
    sales_outlet_id           INTEGER,
    year_month                VARCHAR(255),
    beans_goal                INTEGER,
    beverage_goal             INTEGER,
    food_goal                 INTEGER,
    merchandise_goal          INTEGER,
    total_goal                INTEGER
);

CREATE TABLE SalesOutlet (
    sales_outlet_id           INTEGER,
    sales_outlet_type         VARCHAR(255),
    store_square_feet         INTEGER,
    store_address             VARCHAR(255),
    store_city                VARCHAR(255),
    store_state_province      VARCHAR(255),
    store_telephone           VARCHAR(255),
    store_postal_code         INTEGER,
    store_longitude           FLOAT,
    store_latitude            FLOAT,
    manager                   INTEGER,
    neighbourhood             VARCHAR(255)
);

CREATE TABLE Staff (
    staff_id                  INTEGER,
    first_name                VARCHAR(255),
    last_name                 VARCHAR(255),
    position                  VARCHAR(255),
    start_date                DATE,
    location                  VARCHAR(255)
);


CREATE TABLE SalesReceipts (
    transaction_id            VARCHAR(255),
    transaction_date          DATE,
    transaction_time          VARCHAR(255),
    sales_outlet_id           INTEGER,
    staff_id                  INTEGER,
    customer_id               INTEGER,
    instore_yn                BOOLEAN,
    "order"                   INTEGER,
    line_item_id              INTEGER,
    product_id                INTEGER,
    quantity                  INTEGER,
    line_item_amount          FLOAT,
    unit_price                FLOAT,
    promo_item_yn             BOOLEAN
);

-- Useful commands for CLI manipulation of 
\dt -- shows all tables
select * from customers;

DROP TABLE employees;

ALTER USER leeface WITH SUPERUSER;
\l ## lists database
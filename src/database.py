import psycopg2
from psycopg2.extras import RealDictCursor

class WarehouseDB:
    """Manages PostgreSQL database connections and table migrations."""
    
    def __init__(self, dbname: str = "warehouse_db", user: str = "postgres", password: str = "Ronti@2001", host: str = "localhost", port: str = "5432"):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self._init_schema()

    def get_connection(self):
        """Establishes a connection to PostgreSQL and returns a connection object with RealDictCursor."""
        conn = psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)
        return conn

    def _init_schema(self) -> None:
        """Initializes tables in PostgreSQL with serial keys and foreign key constraints."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS warehouses (
                        warehouse_id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        city VARCHAR(100) NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS products (
                        product_id SERIAL PRIMARY KEY,
                        sku VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(150) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        unit_price NUMERIC(10, 2) CHECK(unit_price >= 0)
                    );

                    CREATE TABLE IF NOT EXISTS inventory (
                        warehouse_id INT REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                        product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                        quantity INT CHECK(quantity >= 0),
                        min_threshold INT DEFAULT 10,
                        PRIMARY KEY (warehouse_id, product_id)
                    );

                    CREATE TABLE IF NOT EXISTS stock_transactions (
                        tx_id SERIAL PRIMARY KEY,
                        product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
                        warehouse_id INT REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                        change_qty INT,
                        tx_type VARCHAR(20) CHECK(tx_type IN ('RESTOCK', 'DISPATCH')),
                        timestamp TIMESTAMP NOT NULL
                    );
                ''')
                conn.commit()
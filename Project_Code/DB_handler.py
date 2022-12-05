
import mysql.connector
import config

DB_USERNAME = config.DB_USERNAME
DB_PASSWORD = config.DB_PASSWORD
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
DB_DATABASENAME = config.DB_DATABASENAME

def connect_to_database():

    # connect to MariaDB platform
    conn = mysql.connector.connect(
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASENAME
    )
    return conn

def create_ad(conn, description, email):
    
    # disable auto-commit
    conn.autocommit = False

    # get cursor
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO advertisement (description, email) VALUES (%s, %s)", (description, email)
    )
    conn.commit()    

    # get ad_id from database
    cur.execute(
        "SELECT LAST_INSERT_ID()"
    )     
    for item in cur:
        last_id = item[0]

    return last_id

def get_state(conn, ad_id):

    # get cursor
    cur = conn.cursor()
    cur.execute(
        "SELECT id, state FROM advertisement WHERE id = %(id)s", {'id':ad_id}
    )
    for item in cur:
        state = item[1]

    return state

def get_ad_data(conn, ad_id):
    
    # get cursor
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, email, category FROM advertisement WHERE id = %(id)s", {'id':ad_id}
    )
    for item in cur:
        description = item[1]
        email = item[2]
        category = item[3]

    return description, email, category

def update_ad_state(conn, ad_id, new_state, category):
    
    # get cursor
    cur = conn.cursor()
    cur.execute(
        "UPDATE advertisement SET state=%(state)s, category=%(category)s WHERE id = %(id)s", {'state':new_state, 'category':category, 'id':ad_id}
    )

    conn.commit()    

def close_connection(conn):
    conn.close()        

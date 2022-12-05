import pika, sys, os
import requests
from S3_handler import download_from_s3_bucket
from DB_handler import connect_to_database, close_connection, update_ad_state, get_ad_data
from image_processing import image_tagging, check_tags
import config

AMQP_URL = config.AMQP_URL
MAILGUN_URL = config.MAILGUN_URL
MAILGUN_API_KEY = config.MAILGUN_API_KEY
MAILGUN_SENDER = config.MAILGUN_SENDER

def send_email(ad_id, email, state):
    
    text = ""
    if(state == 'accepted'):
        text = f"Your ad (id = {ad_id}) has been accepted :)"
    if(state == 'failed'):  
        text = f"Your ad (id = {ad_id}) has not been accepted :("

    return requests.post(
        MAILGUN_URL,
        auth=("api", MAILGUN_API_KEY),
        data={"from": MAILGUN_SENDER,
              "to": email,
              "subject": "Your advertisement state",
              "text": text})

def main():
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()
    channel.queue_declare(queue='id_queue')

    def callback(ch, method, properties, body):
        print("\n")
        print(" [x] Received %r" % body)
        
        current_id = int(str(body)[2:-1])

        # get image from S3 bucket
        download_from_s3_bucket(current_id, 'ad.image')

        # image tagging
        image_tagging_response = image_tagging(current_id)
        state, category = check_tags(image_tagging_response)
        print("     state: " + str(state))
        print("     category: " + str(category))
        os.remove(f"static/downloads/{current_id}.png")

        # update state , category in database
        conn = connect_to_database()
        update_ad_state(conn, current_id, state, category)

        # get email address from database
        email = list(get_ad_data(conn, current_id))[1]
        close_connection(conn)

        # sending email
        send_email_response = send_email(current_id, email, state)
        print("     sending email status: " + str(send_email_response.status_code))

    channel.basic_consume(queue='id_queue', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming() 


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


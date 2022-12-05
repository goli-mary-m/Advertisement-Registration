import os, pika
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from DB_handler import connect_to_database, create_ad, close_connection, get_state, get_ad_data
from S3_handler import upload_to_s3_bucket, download_from_s3_bucket
import config

AMQP_URL = config.AMQP_URL

app = Flask(__name__)
app.config["DEBUG"] = True

# main domain
@app.route("/", methods=["GET"])
def main_page():
    return '''
        <html>
            <body>
                <p><a href="/ad_submission">API-1: ad_submission</a></p>
                <p><a href="/check_state">API-2: check_status</a></p>
            </body>
        </html>
    '''  

# API-1: submit a new advertisement
@app.route("/ad_submission", methods=["GET", "POST"])
def ad_submission_page():

    if request.method == "POST":
        email = request.form["email"]
        description = request.form["description"]
        image = request.files["image"]

        # add data (email & description) to database
        conn = connect_to_database()
        ad_id = create_ad(conn , description, email)
        close_connection(conn)
        
        # add image to S3 bucket
        image_name = '' + str(ad_id) + '.png'
        image.save(os.path.join("static/uploads", secure_filename(image_name)))
        upload_to_s3_bucket(f"static/uploads/{image_name}", 'ad.image', image_name)
        os.remove(f"static/uploads/{image_name}")
        
        # write id on RabbitMQ
        connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        channel = connection.channel()
        channel.queue_declare(queue='id_queue')
        channel.basic_publish(exchange='', routing_key='id_queue', body=str(ad_id))
        connection.close()
        
        return render_template("ad_submission_result.html", ad_id=ad_id, email=email, description=description, image_filename=image.filename)


    return render_template("ad_submission.html")


# API-2: check state of submitted advertisement
@app.route("/check_state", methods=["GET", "POST"])
def check_state_page():

    if request.method == "POST":
        id = request.form["id"]

        # get data (state) from database
        conn = connect_to_database()
        state = get_state(conn, id)
        close_connection(conn)

        # show the result 
        if(state == 'pending'):
            return render_template("check_state_result_pending.html", state=state)

        if(state == 'failed'):
            return render_template("check_state_result_failed.html", state=state)

        if(state == 'accepted'):
            # get data (description, email, category) from database via ad_id
            conn = connect_to_database() 
            description, email, category = get_ad_data(conn, id)
            close_connection(conn)

            # get image from S3 bucket
            download_from_s3_bucket(id, 'ad.image')

            return render_template("check_state_result_accepted.html", state=state, id=id, email=email, category=category, description=description)    


    return render_template("check_state.html")

if __name__ == '__main__':
    app.run()
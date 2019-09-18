from config import Config
from flask import Flask, request

import subprocess
import datetime
import time

app = Flask(__name__)
app.config.from_object(Config)

AuthorsQueue = []
PublicationsQueue = []

InstanceStates = {}

class InstanceState(object):
    def __init__(self, base_mode, special_request_mode=None, special_request_id=None):
        self.base_mode = base_mode
        self.special_request_mode = special_request_mode
        self.special_request_id = special_request_id

def set_instance_state(instance, state):
    InstanceStates[instance] = state

def get_instance_state(instance):
    if instance in InstanceStates:
        return InstanceStates[instance]
    else:
        return None

Address2Name = {}
Name2ExternalAddress = {}
LastUpdateOfAddresses = 0.0

def internal_address_to_instance_name(ip):
    global LastUpdateOfAddresses
    if ip not in Address2Name or time.time() - LastUpdateOfAddresses > 60.0*10.0 :
        p = subprocess.Popen(
            ["gcloud", "compute", "instances", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        (out, err) = p.communicate()

        for line in out.splitlines()[1:]:
            col = line.split()
            ip_internal = col[3]
            ip_external = col[4]
            name = col[0]
            Address2Name[ip_internal] = name
            Name2ExternalAddress[name] = ip_external
        LastUpdateOfAddresses = time.time()
    if ip not in Address2Name:
        return None
    return Address2Name[ip]

def restart_instance(instance):

    p2 = subprocess.Popen(
        ["at", "now", "+", "1", "minute"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # TODO: Zone shouldn't be hard-coded here.
    (out, err) = p2.communicate('gcloud compute instances stop %s --zone us-central1-a  >/home/ubuntu/stoplog.txt 2>&1; sleep 600; gcloud compute instances start %s --zone us-central1-a >/home/ubuntu/startlog.txt 2>&1' % (instance, instance))

    return 'Out: %s\nErr: %s\n' % (out, err)

@app.route("/blocked")
def blocked():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #return 'Your ip is %s.\nYour instance name is %s.\n' % (ip, instance)

    if instance is None:
        message = "Error: Couldn't determine instance name"
        with open('events.txt', 'a') as g:
            g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
        return 'FAIL'

    #message = "Instance blocked. Will restart in one minute."
    message = "Instance blocked. Supervisor will do nothing."
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))

    return 'OK\n'

    # output = restart_instance(instance)
    # return 'Will restart instance %s in one minute.\n"at" output:\n%s' % (
    #     instance, output
    # )

@app.route("/got-cookie")
def got_cookie():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message="Got cookie"
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/crawled/<scholar_id>")
def crawled_publication(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message="Crawled publication %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/crawled-author/<scholar_id>")
def crawled_author(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message="Crawled author %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/added-to-db/<scholar_id>")
def added_publication_to_db(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Added info to db on publication %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/added-author-to-db/<scholar_id>")
def added_author_to_db(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Added info to db on author %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/crawling-failure-author/<scholar_id>/<page>/<reason>")
def crawling_failure_author(scholar_id, page, reason):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Crawling failed for author id %s on %s page, got %s" % (
        scholar_id, page, reason
    )
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-author-canonical-id/<previous>/<canonical>")
def got_author_canonical_id(previous, canonical):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Author with id %s on database has canonical id %s" % (
        previous, canonical
    )
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/started")
def started():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Script starting"
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-stale-publications/<int:count>")
def got_stale_publications(count):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Received %s ids of stale publications from db" % count
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-stale-authors/<int:count>")
def got_stale_authors(count):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Received %s ids of stale authors from db" % count
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-requested-publication/<scholar_id>")
def got_requested_publication(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Received request to crawl publication %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-requested-author/<scholar_id>")
def got_requested_author(scholar_id):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Received request to crawl author %s" % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/crawling-started")
def crawling_started():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Crawling started"
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/got-ip/<external_ip>")
def got_ip(external_ip):
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Got external ip %s" % external_ip
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/exited")
def exited():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = "Script exiting"
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/error", methods=['POST'])
def error():
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = request.form.get("LINE")
    filename = request.form.get("FILENAME")
    command = request.form.get("COMMAND")
    message = "Error on line %s of file %s, Command: %s" % (
        line, filename, command
    )
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/hello", methods=['GET'])
def hello():
    return 'HELLO\n'

@app.route("/poll-command", methods=['GET'])
def poll_command():
    # return 'SET_MODE AUTHOR'
    # return 'SET_MODE PUBLICATION'

    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if AuthorsQueue:
        scholar_id = AuthorsQueue.pop(0)
        command =  'CRAWL_SPECIFIC AUTHOR %s' % scholar_id
    elif PublicationsQueue:
        scholar_id = PublicationsQueue.pop(0)
        command = 'CRAWL_SPECIFIC PUBLICATION %s' % scholar_id
    else:
        command = 'NONE'

    message = "Polled for command, reply: %s" % (
        command
    )
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))

    return command

@app.route("/crawl-request/author/<scholar_id>", methods=['GET'])
def crawl_request_author(scholar_id):
    AuthorsQueue.append(scholar_id)
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'Filed request to crawl author %s' % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'

@app.route("/crawl-request/publication/<scholar_id>", methods=['GET'])
def crawl_request_publication(scholar_id):
    PublicationsQueue.append(scholar_id)
    ip = request.remote_addr
    instance = internal_address_to_instance_name(ip)
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'Filed request to crawl publication %s' % scholar_id
    with open('events.txt', 'a') as g:
        g.write('%s: %s %s %s\n' % (timestr, instance, ip, message))
    return 'OK\n'


if __name__ == '__main__':
    app.run(host=app.config.get('HOST', '0.0.0.0'), port=int(app.config.get('PORT', 4242)))

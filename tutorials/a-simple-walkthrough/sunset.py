import os

import cherrypy
from cherrypy.process.plugins import Daemonizer, PIDFile
import requests

cur_dir = os.path.abspath(os.path.dirname(__file__))
key_path = os.path.join(cur_dir, os.environ.get("SSL_KEY", "key.pem"))
cert_path = os.path.join(cur_dir, os.environ.get("SSL_CRT", "cert.pem"))
astre_svc = os.environ.get("ASTRE_SERVICE", "localhost")
astre_cert_path = os.environ.get("ASTRE_SSL_CRT", "cert.pem")

class Root:
    @cherrypy.expose
    def city(self, name):
        r = requests.post("https://{}:8444/".format(astre_svc), timeout=(2, 2), json={
            "city": name
        }, verify=astre_cert_path)

        if r.status_code != 200:
            raise cherrypy.HTTPError(500, r.text)

        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "The sunset will occur at {} in {}".format(
            r.json()["sunset"], name
        )


def run():

    cherrypy.config.update({
        "environment": "production",
        "log.screen": True,
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8443,
        "server.ssl_module": "builtin",
        "server.ssl_private_key": key_path,
        "server.ssl_certificate": cert_path
    })
    PIDFile(cherrypy.engine, 'sunset.pid').subscribe()
    cherrypy.quickstart(Root())


if __name__ == '__main__':
    run()

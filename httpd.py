# -*- coding: utf-8 -*-

import socketserver
from socket import *
from _thread import *
import threading
import time
import json
import re
import platform
import sys
from time import time, mktime, strftime, sleep
from wsgiref.handlers import format_date_time
from datetime import datetime
import os
from urllib.parse import unquote, urlsplit, parse_qs, parse_qsl
import cgi
from io import BytesIO
import cgi
import logging
from core.confparser import Confparser
from core.compyle import compyle


def millitime():
    return int(round(time() * 1000))

def getcurrentpath():

    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.realpath(__file__))


def get_header(env, param):

    if param in env['request_headers']:
        return env['request_headers'][param]

    return ''


def secure_check(clientsock, env):

    err = 0

    for data in conf.get_all('reject_string'):
        if data in env['request_uri'].lower():
            err = 1

    uri = unquote(env['request_uri'])

    testuri = re.sub(conf.get('restrict_url_chars'), "",  uri)

    if not testuri == uri:
        err = 1

    fnd = 0
    for agent in conf.get_all('allow_agent'):
        if agent.lower() == '*' or agent.lower() in get_header(env, 'User-Agent').lower():
            fnd = 1
    if not fnd:
        err = 1

    if err:
        return 0
    else:
        return 1


def httpdate():

    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def http_options(clientsock, request_headers):

    responseheader = ['HTTP/1.1 200 OK']
    responseheader.append('Date: '+httpdate())
    responseheader.append('Content-Length: 0')
    responseheader.append('Server: '+conf.get('server_version'))
    responseheader.append('Access-Control-Allow-Origin: *')

    if 'Access-Control-Request-Method' in request_headers:
        responseheader.append(
            'Access-Control-Allow-Methods: ' + ', '.join(conf.get_all('allow_method')))
    else:
        responseheader.append(
            'Allow: ' + ', '.join(conf.get_all('allow_method')))

    if 'Access-Control-Request-Headers' in request_headers:
        responseheader.append(
            'Access-Control-Allow-Headers: ' + ', '.join(conf.get_all('allow_header')))
    responseheader.append('Access-Control-Expose-Headers: X-Arc-Set-Session')

    response = '\r\n'.join(responseheader)+'\r\n\r\n'
    bytedata = bytes(response, 'ascii')
    try:
        clientsock.sendall(bytedata)
        clientsock.close()
    except:
        pass


def http_error(clientsock, errorcode):

    error_codes = []
    error_codes.append([400, 'Bad Request'])
    error_codes.append([403, 'Forbidden'])
    error_codes.append([404, 'Not Found'])
    error_codes.append([405, 'Method Not Allowed'])
    error_codes.append([414, 'Request-URI Too Long'])
    error_codes.append([500, 'Internal Server Error'])

    error_string = '500 Internal Server Error'
    for e in error_codes:
        if errorcode == e[0]:
            error_string = str(e[0]) + ' ' + e[1]

    data = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    data += '<html><head><title>' + error_string + '</title></head><body>'
    data += '<h1>' + error_string + '</h1></body></html>'
    data += '<pre>'+httpdate()+'</pre>'

    responseheader = ['HTTP/1.1 '+error_string]
    responseheader.append('Date: '+httpdate())
    responseheader.append('Content-Type: text/html; charset=UTF-8')
    responseheader.append('Content-Length: '+str(len(data)))
    responseheader.append('Server: '+conf.get('server_version'))

    response = '\r\n'.join(responseheader)+'\r\n\r\n'
    response += data + '\r\n'
    bytedata = bytes(response, 'ascii')

    try:
        clientsock.send(bytedata)
        clientsock.close()
    except:
        pass

def process_uri(clientsock, request_headers, request_body, env):

    try:
        uri_max_len = int(conf.get('uri_max_len'))
    except:
        uri_max_len = 512

    if len(request_headers['Request-String']) > uri_max_len:
        return http_error(clientsock, 414)

    tmp = request_headers['Request-String'].split(' ')

    if len(tmp) < 3:
        return http_error(clientsock, 400)

    request_method = tmp[0]
    request_uri = tmp[1]
    request_protocol = tmp[2]

    method_pass = False
    for allowed_method in conf.get_all('allow_method'):
        if allowed_method.lower() == request_method.lower():
            method_pass = True
            break

    if not method_pass:
        return http_error(clientsock, 405)

    request_time = strftime("%Y-%m-%d %H:%M:%S")

    request_uri_parts = urlsplit(request_uri)._asdict()

    """
        http://user:pass@NetLoc:80/sub/path.html;parameters?query=argument#fragment
        scheme  : http
        netloc  : user:pass@NetLoc:80
        path    : /sub/path.html
        params  : parameters
        query   : query=argument
        fragment: fragment
        username: user
        password: pass
        hostname: netloc (netloc in lower case)
        port    : 80
    """

    env['request_uri'] = request_uri
    env['request_uri_parts'] = request_uri_parts
    env['request_uri_dirname'] = os.path.dirname(request_uri_parts['path']).rstrip('/').rstrip('\\')
    env['request_method'] = request_method
    env['request_protocol'] = request_protocol
    env['request_time'] = request_time
    env['request_string'] = request_headers['Request-String']
    env['request_headers'] = request_headers
    env['request_body'] = request_body
    env['remote_addr'] = clientsock.getpeername()[0]
    env['remote_port'] = clientsock.getpeername()[1]
    env['request_get_params'] = dict(parse_qsl(request_uri_parts['query']))
    env['request_post_params'] = {}
    env['request_uploaded_files'] = {}

    if 'Content-Type' in request_headers:

        ctype, pdict = cgi.parse_header(request_headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(
                BytesIO(bytes(request_body, 'utf-8')), pdict)

        elif ctype == 'application/x-www-form-urlencoded':
            postvars = cgi.parse_qs(
                BytesIO(bytes(request_body, 'utf-8')), keep_blank_values=1)

        for v in postvars:
            values = [x.decode('utf-8') for x in postvars[v]]
            if not '[]' in str(v):
                values = values[0]
            env['request_post_params'][str(v)] = values
    
    document_root = conf.get('document_root').replace('%SCRIPT_PATH%',env['script_path'])

    env['session'] = {}
    env['document_root'] = document_root.rstrip('/ ').rstrip('\\ ')
    env['tmp_path'] = conf.get('tmp_path').rstrip('/').rstrip('\\')
    env['session_path'] = conf.get('session_path').rstrip('/').rstrip('\\')
    env['request_file_path'] = env['document_root'] + '/' + request_uri_parts['path'].lstrip('/')
    env['request_file_dir'] = ''
    env['request_file_name'] = ''

    if os.path.isfile(env['request_file_path']):

        env['request_file_name'] = os.path.basename(env['request_file_path'])
        env['request_file_dir'] = os.path.dirname(env['request_file_path'])

    elif os.path.isdir(env['request_file_path']):
        env['request_file_dir'] = env['request_file_path'].rstrip('/')
        for p in conf.get_all('default_page'):
            if os.path.isfile(env['request_file_dir'] + '/' + p):

                env['request_file_path'] = env['request_file_dir'] + '/' + p
                env['request_file_name'] = p

    if env['request_file_name'] == '':
        return http_error(clientsock, 404)

    env['request_file_dir_name'] = env['request_file_dir'].split("/")[-1]
    env['request_file_ext'] = env['request_file_name'].rpartition('.')[2].lower()

    if not secure_check(clientsock, env):
        return http_error(clientsock, 400)
        
    logging.info(env['remote_addr'] + ' - ' + env['request_method'] + ' ' + env['request_uri'] + '"')

    mime_type = conf.get('mime_type_default').strip('"')
    if '.' in env['request_file_name']:
        for m in conf.get_all('mime_type'):
            if ' ' and '"' in m.strip('"'):
                if env['request_file_ext'] == m.partition(' ')[0]:
                    mime_type = m.strip('"').rpartition('"')[2]

    if os.path.isfile(env['request_file_path']):
        try:
            f = open(env['request_file_path'], 'rb')
            data = f.read()
            f.close()
        except Exception as e:
            return http_error(clientsock, 500)
    else:
        return http_error(clientsock, 404)

    custom_headers = {}

    if env['request_file_ext'] in ('py'):
        data, custom_headers, httperror = compyle(data, env)

    # PACK HEDERS

    response_headers = {
        'Date': httpdate(),
        'Content-Type': mime_type,
        'Content-Length': str(len(data)),
        'Server': conf.get('server_version'),
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Expose-Headers': 'X-Arc-Set-Session'
    }

    for m in conf.get_all('max_age_ext'):
        if ' ' in m.strip():
            tmp = m.partition(' ')
            ext = tmp[0]
            age = tmp[2]
            if env['request_file_ext'] == ext:
                response_headers['Cache-Control'] = 'max-age='+age

    if 'Access-Control-Request-Headers' in request_headers:
        response_headers['Access-Control-Allow-Headers'] = ', '.join(
            conf.get_all('allow_header'))

    response_headers.update(custom_headers)

    header_string = 'HTTP/1.1 200 OK\r\n'
    for k in response_headers:
        header_string = header_string + k + ': ' + response_headers[k] + '\r\n'
    header_string = header_string + '\r\n'

    # PACK RESPONSE

    bytedata = bytes(header_string, 'ascii') + data

    try:
        clientsock.sendall(bytedata)
    except Exception as e:
        print("Socket error 14: " + str(e))

    clientsock.close()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):

        data = b''
        content_length = 0
        body_bytes_received = 0
        request_headers = {}
        request_body = b''
        bufsize = 4096

        # To be fixed
        # socket_timeout = int(conf.get('socket_timeout'))
        # self.request.settimeout(socket_timeout)
        
        bytesleft = bufsize
        error = 0

        while True:
            try:
                buf = self.request.recv(bytesleft)
                if buf == b'':
                    error = -1
                    break

                data += buf
                if content_length == 0:

                    if b'\r\n\r\n' in data:

                        # HEADER ANALYSIS

                        parts = data.split(b'\r\n\r\n')
                        raw_header = parts.pop(0).decode('utf-8')
                        request_headers['Raw-Header'] = raw_header
                        method = raw_header.split(' ', 1)[0]
                        headers = raw_header.split('\r\n')
                        request_headers['Request-String'] = headers.pop(0)

                        for h in headers:
                            if ':' in h:
                                key = h.partition(':')[0].strip()
                                val = h.partition(':')[2].strip()
                                request_headers[key] = val

                        if method.lower() == 'options':
                            break

                        if method.lower() == 'get':
                            break

                        if method.lower() == 'post':
                            try:
                                content_length = int(
                                    request_headers['Content-Length'])
                            except Exception as e:
                                error = 400
                                break
                            request_body = b'\r\n\r\n'.join(parts)
                            body_bytes_received = len(request_body)
                            if body_bytes_received >= content_length:
                                break
                            bytesleft = min(
                                bytesleft, content_length-body_bytes_received)

                else:
                    request_body += buf
                    body_bytes_received += len(buf)

                    if body_bytes_received >= content_length:
                        break
                    bytesleft = min(bytesleft, content_length -
                                    body_bytes_received)

            except ConnectionResetError:
                error = -1
            except self.socket.timeout:
                pass

        if error > 0:
            http_error(self.request, error)
        else:
            if not error == -1:
                if method.lower() == 'options':
                    http_options(self.request, request_headers)
                else:
                    process_uri(self.request, request_headers,
                                request_body.decode('utf-8'), self.server.env)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def shutdown():
    print()
    print('    Shutdown..')
    logging.info("Shutdown..")
    server.shutdown()
    server.server_close()

if __name__ == '__main__':

    # https://docs.python.org/3.5/library/socketserver.html#asynchronous-mixins

    print("[-- Simple python web server written by L.Conti (arcaweb) --]")

    conf_path = getcurrentpath() + '/conf/aws.conf'
    if len(sys.argv) > 1:
        conf_path = sys.argv[1]

    conf = Confparser(conf_path)

    # LOGGING
    today = datetime.today()
    log_path = today.strftime(conf.get('log_path').replace('%SCRIPT_PATH%',getcurrentpath()))
    log_level = int(conf.get('log_level'))
    logging.basicConfig(
        filename=log_path,
        filemode='a',
        level=log_level,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    logging.info("Starting HTTPY Server")

    document_root = conf.get('document_root').replace('%SCRIPT_PATH%',getcurrentpath())
    sys.path.append(document_root)
    
    host = conf.get('server_hostname')
    port = int(conf.get('server_port'))
    server_daemon = True if conf.get('server_daemon') == 'true' else False
    server_daemon = False # Daemon mode: to be fixed

    logging.debug("Hostname: "+host)
    logging.debug("port: "+str(port))
    logging.debug("Daemon: "+str(server_daemon))
    logging.debug("Document root: "+document_root)
    
    try:
        server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
        server.env = {'script_path':getcurrentpath()}
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = server_daemon
        server_thread.start()

        print()
        print("    Server running @ http://"+host+':'+str(port))
        print("    Default root:", document_root)
        print()
        if not server_daemon:
            print("    Press CTRL+C or CTRL+BREAK to quit")
        while True:
            try:
                sleep(1)
            except KeyboardInterrupt:
                shutdown()  
                break

    except Exception as e:
        print('    We have a problem: '+str(e))
        logging.critical(str(e))
    
        

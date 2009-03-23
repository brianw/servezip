#!/usr/bin/python

import BaseHTTPServer, SimpleHTTPServer, os, zipfile, tempfile


class ZipRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    server_version = "ZipServer (SimpleHTTP) 0.1"
    
    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and path.endswith('.zip'):
            (ignored, zipname) = os.path.split(path[:-4])
            skiplen = len(zipname) + 4 # filename.zip 
            self.send_zip(path[:-skiplen], zipname)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def send_zip(self, dirname, zipname):
        # Send initial headers
        self.send_response(200)
        self.send_header("Content-type", "application/zip")
        self.send_header("Content-disposition", "attachment; filename=\"%s.zip\"" % zipname)
        # Compress directory structure
        (fd, arcfile) = tempfile.mkstemp('servezip')
        os.close(fd)
        zf = zipfile.ZipFile(arcfile, 'w')
        for root, dirs, filenames in os.walk(dirname):
            for filename in filenames:
                filespec = os.path.join(root, filename)
                arcspec = os.path.join(zipname, filespec.replace(dirname, ''))
                zf.write(filespec, arcspec)
        zf.close()
        # Send content-length header
        arcinfo = os.stat(arcfile)
        self.send_header("Content-length", "%d" % arcinfo.st_size)
        self.end_headers()
        # Send zip data
        sendfile = open(arcfile, "rb")
        self.copyfile(sendfile, self.wfile)
        sendfile.close()
        # Cleanup
        os.unlink(arcfile)
        

if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(('', 8000), ZipRequestHandler)
    print "Ready."
    httpd.serve_forever()
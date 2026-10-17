# Serveur de test avec requêtes Range (206), comme GitHub Pages. Usage : python3 rangesrv.py [port] [dossier]
import sys,os,re,http.server
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
    def end_headers(self):
        self.send_header("Accept-Ranges","bytes");self.send_header("Cache-Control","max-age=600");self.send_header("Access-Control-Allow-Origin","*")
        super().end_headers()
    def send_head(self):
        r=self.headers.get("Range");p=self.translate_path(self.path.split("?")[0])
        if r and os.path.isfile(p):
            m=re.match(r"bytes=(\d*)-(\d*)",r)
            if m:
                size=os.path.getsize(p);a=int(m.group(1)) if m.group(1) else 0;b=int(m.group(2)) if m.group(2) else size-1;b=min(b,size-1)
                if a>b or a>=size:
                    self.send_response(416);self.send_header("Content-Range",f"bytes */{size}");self.end_headers();return None
                f=open(p,"rb");f.seek(a);self.send_response(206);self.send_header("Content-Type",self.guess_type(p));self.send_header("Content-Range",f"bytes {a}-{b}/{size}");self.send_header("Content-Length",str(b-a+1));self.end_headers()
                self._left=b-a+1;return f
        self._left=None;return super().send_head()
    def copyfile(self,src,dst):
        n=getattr(self,"_left",None)
        if n is None:return super().copyfile(src,dst)
        while n>0:
            d=src.read(min(65536,n))
            if not d:break
            dst.write(d);n-=len(d)
if __name__=="__main__":
    port=int(sys.argv[1]) if len(sys.argv)>1 else 8773;os.chdir(sys.argv[2] if len(sys.argv)>2 else ".")
    http.server.ThreadingHTTPServer(("127.0.0.1",port),H).serve_forever()

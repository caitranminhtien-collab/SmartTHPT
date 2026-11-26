import argparse, getpass
from .main import db, init_db, hash_password, Credentials

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['create-admin']);p.add_argument('username');a=p.parse_args()
    password=getpass.getpass('Mật khẩu (ít nhất 8 ký tự): ')
    if password!=getpass.getpass('Nhập lại mật khẩu: '): raise SystemExit('Mật khẩu không khớp')
    Credentials(username=a.username,password=password);init_db()
    with db() as c:
        if c.execute('SELECT 1 FROM users WHERE username=?',(a.username,)).fetchone(): raise SystemExit('Tên đăng nhập đã tồn tại')
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,'admin')",(a.username,hash_password(password)))
    print('Đã tạo quản trị viên.')
if __name__=='__main__': main()

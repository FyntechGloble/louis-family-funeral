import os,sqlite3,hashlib,secrets,hmac,json,time,datetime
from pathlib import Path
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import HTMLResponse,JSONResponse,FileResponse
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from pydantic import BaseModel,Field

DB='/data/family.db'
Path('/data').mkdir(parents=True,exist_ok=True)
SECRET=os.environ.get('APP_SECRET','')
if len(SECRET)<32: raise RuntimeError('APP_SECRET must be at least 32 characters')
signer=URLSafeTimedSerializer(SECRET,salt='family-session-v1')
app=FastAPI(title='Louis Brown Family Memorial Planner',docs_url=None,redoc_url=None)

def conn():
 c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA foreign_keys=ON');return c

def hash_password(password):
 salt=secrets.token_bytes(16);digest=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
 return salt.hex()+':'+digest.hex()
def verify(password,stored):
 try:
  salt,digest=stored.split(':');return hmac.compare_digest(hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=2**14,r=8,p=1),bytes.fromhex(digest))
 except Exception:return False

GROUPS={
 'First priorities':['Confirm hospital release and where Dad is being kept','Appoint funeral director','Contact insurance broker and ask about funeral cover','Confirm death certificate and burial order process','Agree on burial or cremation','Confirm provisional date with pastor and family','Book church or funeral venue','Set budget and coordinate payments','Allocate family responsibilities'],
 'Documents and paperwork':['Collect Dad’s ID','Collect Mom’s ID','Collect contact person’s ID','Obtain medical death notification','Obtain official death certificate','Obtain burial order','Find funeral/insurance policy details','Copy and store important documents'],
 'Funeral director and committal':['Confirm body collection and transportation','Agree on preparation and viewing','Get itemised funeral quote','Select casket or urn','Arrange cemetery plot or crematorium','Complete burial or cremation authorisations','Confirm hearse and family transport'],
 'Church and service':['Confirm officiating pastor','Confirm church capacity, parking and accessibility','Agree on order of service and scripture','Choose worship songs','Arrange family tribute and speakers','Prepare printed programme','Choose memorial photograph and display','Arrange flowers and memorial table','Prepare and test slideshow','Plan livestream and recording','Test audio microphones and screen'],
 'Reception and communication':['Confirm reception venue','Choose catering and estimated headcount','Arrange drinks, tables and serving equipment','Send funeral announcement to family','Confirm ushers and welcome team','Confirm guests needing transport or accessibility help'],
 'Personal memories':['Collect 30–60 photographs','Collect favourite family memories','Write short biography of Dad','Select Dad’s clothing and meaningful items','Decide on private viewing','Prepare tribute honouring Mom and their marriage'],
 'Day before':['Confirm all supplier times and contact numbers','Collect printed programmes','Test music, livestream and presentation','Confirm transport and directions','Reconfirm catering numbers','Send final WhatsApp details','Prepare seating, water and tissues'],
 'Funeral day':['Meet funeral director and venue team','Test equipment before guests arrive','Have ushers welcome guests','Support and privately seat immediate family','Coordinate committal or cemetery departure','Coordinate refreshments','Collect photographs, equipment and belongings'],
 'After funeral':['Send thank-you message','File invoices and payment receipts','Safeguard death certificate and original documents','Follow up with insurance broker','Locate will and executor details','Start estate reporting and bank notifications with authorised representative','Review household affairs with Mom','Save funeral recording and photographs','Plan later memorial or headstone if desired']}

FIELDS=['Funeral date','Service time','Church / venue','Venue address','Pastor','Funeral director','Funeral director phone','Burial or cremation','Committal location','Reception venue','Family coordinator','Livestream link','Family contact number','Notes']
BUDGET=['Funeral director','Casket / urn','Hearse and transport','Cemetery / crematorium','Church / venue','Flowers','Printing','AV / livestream','Catering','Other / contingency']

def setup():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,role TEXT NOT NULL,password TEXT NOT NULL,created TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,category TEXT,title TEXT NOT NULL,done INTEGER DEFAULT 0,assignee INTEGER REFERENCES users(id) ON DELETE SET NULL,notes TEXT DEFAULT '',updated TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '');CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY,title TEXT NOT NULL,estimate REAL NOT NULL DEFAULT 0,actual REAL NOT NULL DEFAULT 0,paid INTEGER NOT NULL DEFAULT 0,notes TEXT DEFAULT '');CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY,actor TEXT,description TEXT,time TEXT DEFAULT CURRENT_TIMESTAMP);''')
  if not c.execute('SELECT COUNT(*) FROM users').fetchone()[0]:
   email=os.environ.get('ADMIN_EMAIL','').strip().lower();pwd=os.environ.get('ADMIN_PASSWORD','')
   if not email or len(pwd)<12:raise RuntimeError('ADMIN_EMAIL and strong ADMIN_PASSWORD (12+ characters) required')
   c.execute('INSERT INTO users(email,name,role,password) VALUES(?,?,?,?)',(email,'Family Administrator','admin',hash_password(pwd)))
  if not c.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]:
   for group,items in GROUPS.items():
    c.executemany('INSERT INTO tasks(category,title) VALUES(?,?)',[(group,item) for item in items])
  for key in FIELDS:c.execute('INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)',(key,''))
  for title in BUDGET:c.execute('INSERT OR IGNORE INTO expenses(title) VALUES(?)',(title,)) if not c.execute('SELECT 1 FROM expenses WHERE title=?',(title,)).fetchone() else None

setup()

def user(request):
 token=request.cookies.get('family_session','')
 try: uid=signer.loads(token,max_age=60*60*24*7)
 except (BadSignature,SignatureExpired):raise HTTPException(401,'Please log in')
 with conn() as c:u=c.execute('SELECT id,name,email,role,password FROM users WHERE id=?',(uid,)).fetchone()
 if not u:raise HTTPException(401,'Please log in')
 return dict(u)

def can_edit(u):return u['role'] in ('admin','coordinator','family')
def require_edit(u):
 if not can_edit(u):raise HTTPException(403,'Read-only access')
def require_admin(u):
 if u['role']!='admin':raise HTTPException(403,'Administrator access required')
def log(c,u,action):c.execute('INSERT INTO activity(actor,description) VALUES(?,?)',(u['name'],action))

@app.middleware('http')
async def security(request:Request,call_next):
 if request.method in ('POST','PUT','PATCH','DELETE'):
  origin=request.headers.get('origin')
  allowed=os.environ.get('ALLOWED_ORIGIN','').rstrip('/')
  if origin and origin.rstrip('/') != allowed: return JSONResponse({'detail':'Invalid request origin'},status_code=403)
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer';response.headers['X-Frame-Options']='DENY'
 response.headers['Cache-Control']='no-store'
 return response

@app.get('/',response_class=HTMLResponse)
def index():return Path('/srv/app/static/index.html').read_text()
@app.get('/manifest.webmanifest')
def manifest():return FileResponse('/srv/app/static/manifest.webmanifest',media_type='application/manifest+json')

class Login(BaseModel):email:str;password:str
@app.post('/api/login')
def login(v:Login):
 with conn() as c:r=c.execute('SELECT * FROM users WHERE email=?',(v.email.lower().strip(),)).fetchone()
 if not r or not verify(v.password,r['password']):raise HTTPException(401,'Incorrect email or password')
 response=JSONResponse({'ok':True})
 response.set_cookie('family_session',signer.dumps(r['id']),httponly=True,secure=os.environ.get('SECURE_COOKIES','true').lower()=='true',samesite='strict',max_age=604800,path='/')
 return response
@app.post('/api/logout')
def logout():
 response=JSONResponse({'ok':True});response.delete_cookie('family_session',path='/');return response
@app.get('/api/state')
def state(request:Request):
 u=user(request)
 with conn() as c:
  return {'me':{k:u[k] for k in ('id','name','role','email')},'users':[dict(r) for r in c.execute('SELECT id,name,email,role FROM users ORDER BY name')], 'tasks':[dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY id')],'settings':{r['key']:r['value'] for r in c.execute('SELECT * FROM settings')},'expenses':[dict(r) for r in c.execute('SELECT * FROM expenses ORDER BY id')],'activity':[dict(r) for r in c.execute('SELECT actor,description,time FROM activity ORDER BY id DESC LIMIT 25')]}
class TaskPatch(BaseModel):done:bool|None=None;assignee:int|None=None;notes:str|None=None;title:str|None=None;category:str|None=None
@app.patch('/api/tasks/{id}')
def task_update(id:int,v:TaskPatch,request:Request):
 u=user(request);require_edit(u)
 with conn() as c:
  task=c.execute('SELECT id FROM tasks WHERE id=?',(id,)).fetchone()
  if not task:raise HTTPException(404,'Task not found')
  changes=v.model_dump(exclude_unset=True)
  if 'done' in changes:changes['done']=int(changes['done'])
  for key in ('title','category','notes'):
   if key in changes:changes[key]=str(changes[key])[:500]
  if 'assignee' in changes and changes['assignee'] is not None and not c.execute('SELECT 1 FROM users WHERE id=?',(changes['assignee'],)).fetchone():raise HTTPException(400,'Unknown family member')
  if changes:
   c.execute('UPDATE tasks SET '+','.join(f'{k}=?' for k in changes)+',updated=CURRENT_TIMESTAMP WHERE id=?',(*changes.values(),id));log(c,u,'Updated checklist item #'+str(id))
 return {'ok':True}
class NewTask(BaseModel):title:str=Field(min_length=2,max_length=300);category:str='Other'
@app.post('/api/tasks')
def task_add(v:NewTask,request:Request):
 u=user(request);require_edit(u)
 with conn() as c:c.execute('INSERT INTO tasks(title,category) VALUES(?,?)',(v.title,v.category[:80]));log(c,u,'Added checklist item')
 return {'ok':True}
@app.delete('/api/tasks/{id}')
def task_del(id:int,request:Request):
 u=user(request);require_admin(u)
 with conn() as c:c.execute('DELETE FROM tasks WHERE id=?',(id,));log(c,u,'Deleted checklist item')
 return {'ok':True}
class Setting(BaseModel):value:str=Field(max_length=5000)
@app.put('/api/settings/{key}')
def setting(key:str,v:Setting,request:Request):
 u=user(request);require_edit(u)
 if key not in FIELDS:raise HTTPException(404,'Unknown field')
 with conn() as c:c.execute('UPDATE settings SET value=? WHERE key=?',(v.value,key));log(c,u,'Updated '+key)
 return {'ok':True}
class ExpensePatch(BaseModel):estimate:float|None=None;actual:float|None=None;paid:bool|None=None;notes:str|None=None
@app.patch('/api/expenses/{id}')
def expense_update(id:int,v:ExpensePatch,request:Request):
 u=user(request);require_edit(u)
 changes=v.model_dump(exclude_unset=True)
 for key in ('estimate','actual'):
  if key in changes and (changes[key]<0 or changes[key]>100000000):raise HTTPException(400,'Invalid amount')
 if 'paid' in changes:changes['paid']=int(changes['paid'])
 if 'notes' in changes:changes['notes']=changes['notes'][:500]
 with conn() as c:
  if not c.execute('SELECT 1 FROM expenses WHERE id=?',(id,)).fetchone():raise HTTPException(404,'Not found')
  if changes:c.execute('UPDATE expenses SET '+','.join(f'{k}=?' for k in changes)+' WHERE id=?',(*changes.values(),id));log(c,u,'Updated budget item #'+str(id))
 return {'ok':True}
class Member(BaseModel):name:str=Field(min_length=2,max_length=100);email:str;role:str='family'
@app.post('/api/members')
def member_add(v:Member,request:Request):
 u=user(request);require_admin(u)
 if v.role not in ('admin','coordinator','family','viewer'):raise HTTPException(400,'Invalid role')
 pwd=secrets.token_urlsafe(18)
 try:
  with conn() as c:c.execute('INSERT INTO users(email,name,role,password) VALUES(?,?,?,?)',(v.email.lower().strip(),v.name,v.role,hash_password(pwd)));log(c,u,'Invited '+v.name)
 except sqlite3.IntegrityError:raise HTTPException(409,'Email already registered')
 return {'temporary_password':pwd,'message':'Share privately; password is shown once'}
class NewPassword(BaseModel):old:str;new:str=Field(min_length=12,max_length=128)
@app.post('/api/password')
def password_change(v:NewPassword,request:Request):
 u=user(request)
 if not verify(v.old,u['password']):raise HTTPException(400,'Current password incorrect')
 with conn() as c:c.execute('UPDATE users SET password=? WHERE id=?',(hash_password(v.new),u['id']));log(c,u,'Changed password')
 return {'ok':True}

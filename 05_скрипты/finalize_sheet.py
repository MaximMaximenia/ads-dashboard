import json,os,urllib.parse,urllib.request,urllib.error
K=os.path.expanduser('~/Desktop/Реклама/04_ключи/google_sheets_token.json'); c=json.load(open(K))
tok=json.load(urllib.request.urlopen(urllib.request.Request(c['token_uri'],data=urllib.parse.urlencode({'client_id':c['client_id'],'client_secret':c['client_secret'],'refresh_token':c['refresh_token'],'grant_type':'refresh_token'}).encode())))
AT=tok['access_token']; SID='1HJOma0g319T6tJ-nPuxWHz_MNrKV2bnFzELKyC95XWA'
def api(url,method='GET',body=None):
 req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Authorization':'Bearer '+AT,'Content-Type':'application/json'})
 try: return json.load(urllib.request.urlopen(req,timeout=60))
 except urllib.error.HTTPError as e: print('ERR',e.code,e.read().decode()[:600]); return None
# total row
vals=[['ИТОГО','','','','','',540,238,119]]
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}/values/{urllib.parse.quote("Звонки 26.10!A55:I55",safe="")}?valueInputOption=USER_ENTERED','PUT',{'values':vals})
# styles merge + dark
reqs=[{'mergeCells':{'range':{'sheetId':0,'startRowIndex':54,'endRowIndex':55,'startColumnIndex':0,'endColumnIndex':6},'mergeType':'MERGE_ALL'}},
{'repeatCell':{'range':{'sheetId':0,'startRowIndex':54,'endRowIndex':55,'startColumnIndex':0,'endColumnIndex':9},'cell':{'userEnteredFormat':{'backgroundColor':{'red':0x17/255,'green':0x18/255,'blue':0x1a/255},'textFormat':{'foregroundColor':{'red':1,'green':1,'blue':1},'bold':True,'fontSize':9},'numberFormat':{'type':'NUMBER','pattern':'#,##0'}}},'fields':'userEnteredFormat(backgroundColor,textFormat,numberFormat)'}}]
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}:batchUpdate','POST',{'requests':reqs})
# permissions: make anyone writer
p=api(f'https://www.googleapis.com/drive/v3/files/{SID}/permissions?fields=permissions(id,type,role)')
print('perms',p)
if p:
 for it in p.get('permissions',[]):
  if it.get('type')=='anyone':
   api(f'https://www.googleapis.com/drive/v3/files/{SID}/permissions/{it["id"]}?fields=id,role','PATCH',{'role':'writer'})
print('done')

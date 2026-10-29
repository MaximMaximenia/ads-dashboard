import json,os,urllib.parse,urllib.request
K=os.path.expanduser('~/Desktop/Реклама/04_ключи/google_sheets_token.json'); c=json.load(open(K))
tok=json.load(urllib.request.urlopen(urllib.request.Request(c['token_uri'],data=urllib.parse.urlencode({'client_id':c['client_id'],'client_secret':c['client_secret'],'refresh_token':c['refresh_token'],'grant_type':'refresh_token'}).encode())))
AT=tok['access_token']; SID='1HJOma0g319T6tJ-nPuxWHz_MNrKV2bnFzELKyC95XWA'
def api(url,method='GET',body=None):
 req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Authorization':'Bearer '+AT,'Content-Type':'application/json'})
 try: return json.load(urllib.request.urlopen(req,timeout=60))
 except Exception as e:
  print('ERR',e); return None
rows=json.load(open('/Users/maksim/Desktop/Реклама/06_звонки/27.10.2026/rows_27.json'))
head=['Время','Длит.','Телефон','Тема','Статус','Комментарий','Цена, BYN']
vals=[head]+rows+[['ИТОГО','','','','','','=SUM(G2:G44)']]
# add sheet
r=api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}:batchUpdate','POST',{'requests':[{'addSheet':{'properties':{'title':'Звонки 27.10','gridProperties':{'rowCount':60,'columnCount':7}}}}]})
gid=r['replies'][0]['addSheet']['properties']['sheetId']
print('gid',gid)
# values
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}/values/'+urllib.parse.quote('Звонки 27.10!A1:G45',safe='')+'?valueInputOption=USER_ENTERED','PUT',{'values':vals})
# formatting
def col(h):
 h=h.lstrip('#'); return {'red':int(h[0:2],16)/255,'green':int(h[2:4],16)/255,'blue':int(h[4:6],16)/255}
reqs=[]; reqs.append({'setBasicFilter':{'filter':{'range':{'sheetId':gid,'startRowIndex':0,'endRowIndex':44,'startColumnIndex':0,'endColumnIndex':7}}}})
reqs.append({'updateSheetProperties':{'properties':{'sheetId':gid,'gridProperties':{'frozenRowCount':1}},'fields':'gridProperties.frozenRowCount'}})
reqs.append({'repeatCell':{'range':{'sheetId':gid,'startRowIndex':0,'endRowIndex':1,'startColumnIndex':0,'endColumnIndex':7},'cell':{'userEnteredFormat':{'backgroundColor':col('17181A'),'textFormat':{'foregroundColor':col('FFFFFF'),'bold':True,'fontSize':9},'horizontalAlignment':'CENTER','verticalAlignment':'MIDDLE'}},'fields':'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'}})
# all data white
reqs.append({'repeatCell':{'range':{'sheetId':gid,'startRowIndex':1,'endRowIndex':44,'startColumnIndex':0,'endColumnIndex':7},'cell':{'userEnteredFormat':{'backgroundColor':col('FFFFFF'),'textFormat':{'foregroundColor':col('000000'),'fontSize':9},'verticalAlignment':'MIDDLE','wrapStrategy':'WRAP'}},'fields':'userEnteredFormat(backgroundColor,textFormat,verticalAlignment,wrapStrategy)'}})
# total
reqs.append({'mergeCells':{'range':{'sheetId':gid,'startRowIndex':44,'endRowIndex':45,'startColumnIndex':0,'endColumnIndex':6},'mergeType':'MERGE_ALL'}})
reqs.append({'repeatCell':{'range':{'sheetId':gid,'startRowIndex':44,'endRowIndex':45,'startColumnIndex':0,'endColumnIndex':7},'cell':{'userEnteredFormat':{'backgroundColor':col('17181A'),'textFormat':{'foregroundColor':col('FFFFFF'),'bold':True,'fontSize':9}}},'fields':'userEnteredFormat(backgroundColor,textFormat)'}})
# widths
for i,w in enumerate([80,70,140,220,160,360,100]):
 reqs.append({'updateDimensionProperties':{'range':{'sheetId':gid,'dimension':'COLUMNS','startIndex':i,'endIndex':i+1},'properties':{'pixelSize':w},'fields':'pixelSize'}})
# validation
statuses=['Приедет','Под вопросом','Недозвон','Не по теме','Старый / не по теме']
reqs.append({'setDataValidation':{'range':{'sheetId':gid,'startRowIndex':1,'endRowIndex':44,'startColumnIndex':4,'endColumnIndex':5},'rule':{'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':s} for s in statuses]},'showCustomUi':True,'strict':False}}})
# CF green/yellow
for s,bg,fg in [('Приедет','C6EFCE','006100'),('Под вопросом','FFEB9C','9C6500')]:
 reqs.append({'addConditionalFormatRule':{'rule':{'ranges':[{'sheetId':gid,'startRowIndex':1,'endRowIndex':44,'startColumnIndex':0,'endColumnIndex':7}],'booleanRule':{'condition':{'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':f'=$E2="{s}"'}]},'format':{'backgroundColor':col(bg),'textFormat':{'foregroundColor':col(fg)}}}},'index':0}})
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}:batchUpdate','POST',{'requests':reqs})
# summary two days
summary=[
 ['ДАСТО — звонки 26–27.10.2026','','','','','','','','','',''],
 ['Входящие из A1 ВАТС. Статусы/расшифровка — предварительные.','','','','','','','','','',''],
 ['День','Входящие','Уникальные','Приедет','Под вопросом','Не по теме','Недозвон','Сумма цен, BYN','Реклама, $','Реклама, BYN','Остаток, BYN'],
 ['26.10',53,42,14,26,7,6,"=SUM('Звонки 26.10'!G2:G54)",30.11,90.33,'=H4-J4'],
 ['27.10',43,34,1,29,5,8,"=SUM('Звонки 27.10'!G2:G44)",34.40,103.21,'=H5-J5'],
 ['Итого',96,67,15,55,12,14,'=H4+H5','=I4+I5','=J4+J5','=H6-J6'],
 ['','','','','','','','','','',''],
 ['Сумма цен — только по заполненным ценам. 27.10 — предварительно, часть расшифровки не удалась.','','','','','','','','','',''],
]
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}/values/'+urllib.parse.quote('Сводка!A1:K8',safe='')+'?valueInputOption=USER_ENTERED','PUT',{'values':summary})
# summary styles
s_id=1451654638
reqs=[
 {'repeatCell':{'range':{'sheetId':s_id,'startRowIndex':2,'endRowIndex':3,'startColumnIndex':0,'endColumnIndex':11},'cell':{'userEnteredFormat':{'backgroundColor':col('17181A'),'textFormat':{'foregroundColor':col('FFFFFF'),'bold':True,'fontSize':9},'horizontalAlignment':'CENTER','verticalAlignment':'MIDDLE'}},'fields':'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'}},
 {'repeatCell':{'range':{'sheetId':s_id,'startRowIndex':5,'endRowIndex':6,'startColumnIndex':0,'endColumnIndex':11},'cell':{'userEnteredFormat':{'backgroundColor':col('E7E6E6'),'textFormat':{'bold':True,'fontSize':9}}},'fields':'userEnteredFormat(backgroundColor,textFormat)'}},
]
for i,w in enumerate([90,80,80,80,90,80,80,120,90,100,100]):
 reqs.append({'updateDimensionProperties':{'range':{'sheetId':s_id,'dimension':'COLUMNS','startIndex':i,'endIndex':i+1},'properties':{'pixelSize':w},'fields':'pixelSize'}})
api(f'https://sheets.googleapis.com/v4/spreadsheets/{SID}:batchUpdate','POST',{'requests':reqs})
print('done')

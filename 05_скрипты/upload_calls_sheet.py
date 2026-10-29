import json, os, urllib.parse, urllib.request, urllib.error, openpyxl, math
K=os.path.expanduser('~/Desktop/Реклама/04_ключи/google_sheets_token.json')
c=json.load(open(K))
tok=json.load(urllib.request.urlopen(urllib.request.Request(c['token_uri'],data=urllib.parse.urlencode({
 'client_id':c['client_id'],'client_secret':c['client_secret'],'refresh_token':c['refresh_token'],'grant_type':'refresh_token'}).encode())))
AT=tok['access_token']
def api(url,method='GET',body=None):
 req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,method=method,
  headers={'Authorization':'Bearer '+AT,'Content-Type':'application/json'})
 try: return json.load(urllib.request.urlopen(req,timeout=60))
 except urllib.error.HTTPError as e:
  print('ERR',e.code,e.read().decode()[:1000]); raise

src='/Users/maksim/Desktop/Реклама/03_анализ/Звонки_ДАСТО_26.10.2026.xlsx'
wb=openpyxl.load_workbook(src,data_only=False); ws=wb['Звонки 26.10']
rows=[]
for r in range(2,ws.max_row):
    vals=[ws.cell(r,c).value for c in range(1,7)]
    if not vals[0]: continue
    status=vals[4]; topic=vals[3] or ''
    price=80 if 'Развал' in topic else (30 if 'Регулировка' in topic else None)
    rev=round(price*0.7) if (price and status=='Приедет') else 0
    pot=round(price*0.7) if (price and status=='Под вопросом') else 0
    rows.append(vals+[price,rev,pot])
print('rows',len(rows))
# create
sh=api('https://sheets.googleapis.com/v4/spreadsheets','POST',{
 'properties':{'title':'ДАСТО — звонки 26.10.2026','locale':'ru_RU','timeZone':'Asia/Minsk'},
 'sheets':[{'properties':{'title':'Звонки 26.10','gridProperties':{'rowCount':max(60,len(rows)+8),'columnCount':9}}},
           {'properties':{'title':'Сводка','gridProperties':{'rowCount':40,'columnCount':4}}},
           {'properties':{'title':'Как заполнять','gridProperties':{'rowCount':20,'columnCount':2}}}]})
sid=sh['spreadsheetId']; url=sh['spreadsheetUrl']; print('created',url)
# values
head=['Время','Длит.','Телефон','Тема','Статус','Комментарий','Цена, BYN','Выручка (70%), BYN','Потенциал (70%), BYN']
vals=[head]+rows
api(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{urllib.parse.quote("Звонки 26.10!A1:I"+str(len(vals)),safe="")}?valueInputOption=USER_ENTERED','PUT',{'values':vals})
# summary
cnt={k:sum(1 for r in rows if r[4]==k) for k in ['Приедет','Под вопросом','Недозвон','Не по теме','Старый / не по теме']}
rev=sum(r[7] for r in rows); pot=sum(r[8] for r in rows); priced=sum(1 for r in rows if r[6])
s=[['ДАСТО — звонки 26.10.2026',''],['Входящие из A1 ВАТС. Статусы/расшифровка — предварительные.',''],['',''],
   ['Показатель','Значение'],
   ['Всего входящих звонков',len(rows)],
   ['Уникальных номеров',len({r[2] for r in rows})],
   ['Приедет',cnt['Приедет']],
   ['Под вопросом',cnt['Под вопросом']],
   ['Недозвон',cnt['Недозвон']],
   ['Не по теме / старые',cnt['Не по теме']+cnt['Старый / не по теме']],
   ['',''],
   ['Ожидаемая выручка по известным ценам, BYN',rev],
   ['Потенциал по «под вопросом» (известные цены), BYN',pot],
   ['Заполнено цен, шт.',priced],
   ['',''],
   ['70% — доля доезжаемости. Выручка = цена × 0,7 только для «Приедет».',''],
   ['Развал: 80 BYN (60–100). Регулировка фар: 30 BYN. Остальные цены — заполнить.','']]
api(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{urllib.parse.quote("Сводка!A1:B"+str(len(s)),safe="")}?valueInputOption=USER_ENTERED','PUT',{'values':s})
readme=[['Как заполнять таблицу'],[''],
 ['1. Колонка G «Цена, BYN» — цена услуги. Развал 80 (60–100), регулировка фар 30.'],
 ['2. H — ожидаемая выручка по «Приедет» (70%); I — потенциал по «Под вопросом».'],
 ['3. Для остальных услуг (масло, подвеска, тормоза, глушитель и т.д.) впишите цену в G.'],
 ['4. Статусы: зелёный — приедет, жёлтый — под вопросом, серый — недозвон, красный — не по теме, оранжевый — старый.'],
 ['5. Итог — внизу листа «Звонки 26.10» и на «Сводке».']]
api(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{urllib.parse.quote("Как заполнять!A1:A"+str(len(readme)),safe="")}?valueInputOption=USER_ENTERED','PUT',{'values':readme})
# formatting
sheet_ids={s['properties']['title']:s['properties']['sheetId'] for s in sh['sheets']}
sid0=sheet_ids['Звонки 26.10']; sid1=sheet_ids['Сводка']; sid2=sheet_ids['Как заполнять']
def color(hexv):
 hexv=hexv.lstrip('#'); return {'red':int(hexv[0:2],16)/255,'green':int(hexv[2:4],16)/255,'blue':int(hexv[4:6],16)/255}
reqs=[]
# freeze + filter
reqs.append({'updateSheetProperties':{'properties':{'sheetId':sid0,'gridProperties':{'frozenRowCount':1}},'fields':'gridProperties.frozenRowCount'}})
reqs.append({'setBasicFilter':{'filter':{'range':{'sheetId':sid0,'startRowIndex':0,'endRowIndex':len(vals),'startColumnIndex':0,'endColumnIndex':9}}}})
# header
reqs.append({'repeatCell':{'range':{'sheetId':sid0,'startRowIndex':0,'endRowIndex':1,'startColumnIndex':0,'endColumnIndex':9},'cell':{'userEnteredFormat':{'backgroundColor':color('17181A'),'textFormat':{'foregroundColor':color('FFFFFF'),'bold':True,'fontSize':9},'horizontalAlignment':'CENTER','verticalAlignment':'MIDDLE'}},'fields':'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'}})
fills={'Приедет':('C6EFCE','006100'),'Под вопросом':('FFEB9C','9C6500'),'Недозвон':('D9D9D9','404040'),'Не по теме':('FFC7CE','9C0006'),'Старый / не по теме':('FCE4D6','833C00')}
for i,r in enumerate(rows,1):
 bg,fg=fills.get(r[4],('FFFFFF','000000'))
 reqs.append({'repeatCell':{'range':{'sheetId':sid0,'startRowIndex':i,'endRowIndex':i+1,'startColumnIndex':0,'endColumnIndex':9},'cell':{'userEnteredFormat':{'backgroundColor':color(bg),'textFormat':{'foregroundColor':color(fg),'fontSize':9},'verticalAlignment':'MIDDLE','wrapStrategy':'WRAP'}},'fields':'userEnteredFormat(backgroundColor,textFormat,verticalAlignment,wrapStrategy)'}})
# number format G:I
reqs.append({'repeatCell':{'range':{'sheetId':sid0,'startRowIndex':1,'endRowIndex':len(vals),'startColumnIndex':6,'endColumnIndex':9},'cell':{'userEnteredFormat':{'numberFormat':{'type':'NUMBER','pattern':'#,##0'}}},'fields':'userEnteredFormat.numberFormat'}})
# widths
widths=[80,70,140,220,160,360,100,130,140]
for i,w in enumerate(widths):
 reqs.append({'updateDimensionProperties':{'range':{'sheetId':sid0,'dimension':'COLUMNS','startIndex':i,'endIndex':i+1},'properties':{'pixelSize':w},'fields':'pixelSize'}})
# total row style
tr=len(vals)
reqs.append({'repeatCell':{'range':{'sheetId':sid0,'startRowIndex':tr-1,'endRowIndex':tr,'startColumnIndex':0,'endColumnIndex':9},'cell':{'userEnteredFormat':{'backgroundColor':color('17181A'),'textFormat':{'foregroundColor':color('FFFFFF'),'bold':True,'fontSize':9}}},'fields':'userEnteredFormat(backgroundColor,textFormat)'}})
# summary styles
reqs.append({'repeatCell':{'range':{'sheetId':sid1,'startRowIndex':3,'endRowIndex':4,'startColumnIndex':0,'endColumnIndex':2},'cell':{'userEnteredFormat':{'backgroundColor':color('17181A'),'textFormat':{'foregroundColor':color('FFFFFF'),'bold':True}}},'fields':'userEnteredFormat(backgroundColor,textFormat)'}})
reqs.append({'updateDimensionProperties':{'range':{'sheetId':sid1,'dimension':'COLUMNS','startIndex':0,'endIndex':1},'properties':{'pixelSize':520},'fields':'pixelSize'}})
reqs.append({'updateDimensionProperties':{'range':{'sheetId':sid1,'dimension':'COLUMNS','startIndex':1,'endIndex':2},'properties':{'pixelSize':120},'fields':'pixelSize'}})
reqs.append({'updateDimensionProperties':{'range':{'sheetId':sid2,'dimension':'COLUMNS','startIndex':0,'endIndex':1},'properties':{'pixelSize':800},'fields':'pixelSize'}})
api(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}:batchUpdate','POST',{'requests':reqs})
# share anyone reader (drive.file)
try:
 api(f'https://www.googleapis.com/drive/v3/files/{sid}/permissions?sendNotificationEmail=false','POST',{'role':'reader','type':'anyone'})
 print('shared anyone reader')
except Exception as e: print('share failed',e)
print('URL',url)
json.dump({'id':sid,'url':url},open('/Users/maksim/Desktop/Реклама/03_анализ/last_sheet.json','w'),ensure_ascii=False,indent=1)

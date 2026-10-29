import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
p='/Users/maksim/Desktop/Реклама/03_анализ/Звонки_ДАСТО_26.10.2026.xlsx'
wb=openpyxl.load_workbook(p)
ws=wb['Звонки 26.10']
# delete H:I
ws.delete_cols(8,2)
# prices only for booked
for r in range(2,55):
    status=ws.cell(r,5).value; topic=ws.cell(r,4).value or ''
    price=45 if (status=='Приедет' and 'Регулировка' in topic) else (80 if (status=='Приедет' and 'Развал' in topic) else None)
    ws.cell(r,7).value=price
    ws.cell(r,7).number_format='#,##0'
# header G
c=ws.cell(1,7); c.value='Цена, BYN'; c.fill=PatternFill('solid',fgColor='17181A'); c.font=Font(color='FFFFFF',bold=True,size=10); c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
# total row 55
ws.cell(55,1,'ИТОГО')
ws.merge_cells(start_row=55,start_column=1,end_row=55,end_column=6)
ws.cell(55,1).alignment=Alignment(horizontal='right',vertical='center')
ws.cell(55,7).value='=SUM(G2:G54)'; ws.cell(55,7).number_format='#,##0'
for c in range(1,8):
    ws.cell(55,c).fill=PatternFill('solid',fgColor='17181A'); ws.cell(55,c).font=Font(color='FFFFFF',bold=True,size=10)
ws.column_dimensions['G'].width=12
# summary rebuild
if 'Сводка' in wb.sheetnames: del wb['Сводка']
if 'Как заполнять' in wb.sheetnames: del wb['Как заполнять']
s=wb.create_sheet('Сводка',1)
s['A1']='ДАСТО — звонки 26.10.2026'; s['A1'].font=Font(size=18,bold=True)
s['A2']='Входящие из A1 ВАТС. Статусы/расшифровка — предварительные.'; s['A2'].font=Font(size=10,color='6E6E73')
r=4
s.cell(r,1,'Показатель').font=Font(bold=True,color='FFFFFF'); s.cell(r,1).fill=PatternFill('solid',fgColor='17181A')
s.cell(r,2,'Значение').font=Font(bold=True,color='FFFFFF'); s.cell(r,2).fill=PatternFill('solid',fgColor='17181A')
r+=1
def add(k,v,fmt=None,bold=False):
    global r
    s.cell(r,1,k).font=Font(bold=bold); s.cell(r,2,v).font=Font(bold=bold)
    if fmt: s.cell(r,2).number_format=fmt
    r+=1
add('Всего входящих звонков',53)
add('Уникальных номеров',42)
add('Приедет',14,bold=True)
add('Под вопросом',26)
add('Не по теме',7)
add('Недозвон',6)
r+=1
add('Сумма цен по «Приедет» (заполненные), BYN','=SUM(\'Звонки 26.10\'!G2:G54)','#,##0',True)
add('Расход на рекламу 26.10, $',30.11,'$#,##0.00')
add('Расход на рекламу, BYN (≈3,0)',90.33,'#,##0.00')
add('Остаток после рекламы, BYN','=B13-B15','#,##0',True)
r+=1
s.cell(r,1,'Сумма считается только по заполненным ценам. Остальные цены — в колонке G.').font=Font(size=9,color='6E6E73')
s.column_dimensions['A'].width=58; s.column_dimensions['B'].width=16
for rr in range(4,r+1):
    s.cell(rr,1).alignment=Alignment(vertical='center',wrap_text=True)
    s.cell(rr,2).alignment=Alignment(vertical='center')
wb.save(p)
print('saved',p)

import json
from pathlib import Path
import streamlit as st

FILE = Path(__file__).with_name('vardiya_data.json')
SHIFTS = {'V1': '07:00 - 15:00', 'V2': '15:00 - 23:00', 'V3': '23:00 - 07:00', 'Normal': '08:30 - 18:00'}

def load():
    if not FILE.exists():
        FILE.write_text(json.dumps({'people': [], 'overrides': {}}, ensure_ascii=False), encoding='utf-8')
    return json.loads(FILE.read_text(encoding='utf-8'))

def save(data):
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def automatic(person, week):
    if person['start'] == 'Normal': return 'Normal'
    return f"V{((int(person['start'][1:]) - 1 + week - 1) % 3) + 1}"

st.set_page_config(page_title='Sirius Vardiya Yönetimi', layout='wide')
data = load()
st.title('SIRIUS VARDİYA YÖNETİMİ')
st.caption('Personel ekleme, otomatik rotasyon ve manuel vardiya müdahalesi')
plan, people, settings = st.tabs(['Vardiya Kutuları', 'Personel Yönetimi', 'Ayarlar'])

with plan:
    week = st.number_input('Hafta', 1, 52, 1)
    active = [p for p in data['people'] if p.get('active', True)]
    cols = st.columns(4)
    for col, shift in zip(cols, SHIFTS):
        with col:
            st.subheader(f'{shift}  |  {SHIFTS[shift]}')
            for p in active:
                key = f"{p['name']}|{week}"
                final = data['overrides'].get(key, automatic(p, week))
                if final == shift: st.info(f"**{p['name']}**\n\n{p['position']}")
    st.subheader('Manuel Müdahale')
    for i, p in enumerate(active):
        a, b, c = st.columns([3, 2, 2]); a.write(p['name']); b.write(p['position'])
        key = f"{p['name']}|{week}"; options = ['Otomatik'] + list(SHIFTS); old = data['overrides'].get(key, 'Otomatik')
        choice = c.selectbox('Vardiya', options, index=options.index(old), key=f'm_{i}_{week}')
        if choice == 'Otomatik': data['overrides'].pop(key, None)
        else: data['overrides'][key] = choice
    if st.button('Değişiklikleri Kaydet', type='primary'): save(data); st.success('Plan kaydedildi.'); st.rerun()

with people:
    st.subheader('Personel Ekle')
    a, b, c, d = st.columns([3, 2, 1, 1]); name = a.text_input('Ad Soyad'); position = b.text_input('Pozisyon'); start = c.selectbox('Başlangıç', list(SHIFTS))
    if d.button('Ekle') and name.strip(): data['people'].append({'name': name.strip(), 'position': position.strip(), 'start': start, 'active': True}); save(data); st.rerun()
    st.subheader('Personel Listesi')
    for i, p in enumerate(data['people']):
        a, b, c = st.columns([3, 2, 1]); a.write(p['name']); b.write(p['position']); p['active'] = c.checkbox('Aktif', p.get('active', True), key=f'a_{i}')
    if st.button('Personel Durumlarını Kaydet'): save(data); st.success('Kaydedildi.')

with settings:
    st.subheader('Vardiya Ayarları')
    for key, value in SHIFTS.items(): st.write(f'**{key}:** {value}')
    st.write('Otomatik rotasyon: V1 → V2 → V3. Normal vardiya rotasyona girmez.')

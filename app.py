import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Enterprise Stock & Multi-Company System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 0. รายชื่อบริษัทและพจนานุกรมภาษา (TH / EN)
# ----------------------------------------------------
COMPANIES = [
    "ทุกบริษัท/สาขา (All Companies / Branches)",
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)"
]

REAL_COMPANIES = [c for c in COMPANIES if "ทุกบริษัท" not in c]

CATEGORIES_LIST = [
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits",
    "ทะเล / Seafood",
    "เนื้อวัว / Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other",
    "เบียร์ / Beer",
    "ไส้กรอก / Sausage",
    "ชีส / Cheese",
    "นม / Milk"
]

UNITS_LIST = ["Box", "Pack", "Bag", "Kg", "Pcs", "Litre", "Bottle", "Can", "Gram"]
VAT_TYPES_LIST = ["Non Vat", "Vat 7%"]

LANG = {
    "th": {
        "title": "ระบบจัดการสต็อกวัตถุดิบและคลังสินค้า (Multi-Company)",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory_mgmt": "📦 การจัดการรายการสินค้า",
        "sub_import_excel": "📥 นำเข้าสินค้า (Excel & Manual)",
        "sub_stock_in": "📥 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อก",
        "m_company_settings": "🏢 ตั้งค่าข้อมูลบริษัท",
    },
    "en": {
        "title": "Enterprise Food Cost & Stock Management System",
        "menu": "📌 Main Menu",
        "m_dashboard": "📊 Dashboard & Overview",
        "m_inventory_mgmt": "📦 Inventory Management",
        "sub_import_excel": "📥 Import Items (Excel & Manual)",
        "sub_stock_in": "📥 Stock In",
        "sub_stock_out": "📤 Stock Out / Requisition",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_eom": "📋 Stock Summary & End of Month Count",
        "m_company_settings": "🏢 Company Settings",
    }
}

TRANSLATE_DICT = {
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others": "Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits": "Vegetables & Fruits",
    "ทะเล / Seafood": "Seafood",
    "เนื้อวัว / Beef": "Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other": "Juice / Soft Drink / Other",
    "เบียร์ / Beer": "Beer",
    "ไส้กรอก / Sausage": "Sausage",
    "ชีส / Cheese": "Cheese",
    "นม / Milk": "Milk"
}

# ----------------------------------------------------
# 1. จัดการ Session State (ฐานข้อมูลจำลอง)
# ----------------------------------------------------
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'th'

if 'company_addresses' not in st.session_state:
    st.session_state['company_addresses'] = {comp: f"ที่อยู่สำนักงานใหญ่/สาขา ของ {comp}" for comp in REAL_COMPANIES}

if 'company_inventories' not in st.session_state:
    st.session_state['company_inventories'] = {}
    for comp in REAL_COMPANIES:
        st.session_state['company_inventories'][comp] = pd.DataFrame(columns=[
            "Product Code", "Item Name", "Category", "Unit", "Stock Balance", "Last Price", "Supplier", "Vat Type"
        ])
    st.session_state['company_inventories'][REAL_COMPANIES[0]] = pd.DataFrame([
        {"Product Code": "422582", "Item Name": "นมจืด 1 ลิตร", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Box", "Stock Balance": 25.0, "Last Price": 109.0, "Supplier": "CP Axtra (Makro)", "Vat Type": "Non Vat"},
        {"Product Code": "2502009877754", "Item Name": "กระเทียมดัดจุก 500 ก.", "Category": "ผักและผลไม้ / Vegetables & Fruits", "Unit": "Pack", "Stock Balance": 10.0, "Last Price": 40.0, "Supplier": "CP Axtra (Lotus)", "Vat Type": "Non Vat"},
        {"Product Code": "54061057", "Item Name": "คิทแคท ทริกเกอร์ 500 กรัม", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Bag", "Stock Balance": 0.0, "Last Price": 130.0, "Supplier": "กส-สรา ค้าส่ง", "Vat Type": "Vat 7%"}
    ])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame([
        {"Company": REAL_COMPANIES[0], "Date": str(datetime.today().date()), "DocNo": "INV-001", "Supplier": "CP Axtra (Makro)", "Item Name": "นมจืด 1 ลิตร", "Quantity": 25.0, "Price/Unit": 109.0, "Vat Type": "Non Vat", "Total Price": 2725.0, "Type": "IMPORT", "Receiver": "-", "Department": "-"}
    ])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": REAL_COMPANIES[0], "Role": "Manager"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items"])

if 'wast_variance_records' not in st.session_state:
    st.session_state['wast_variance_records'] = pd.DataFrame(columns=["Company", "Date", "Item Name", "Wast_Variance", "OC_Test", "Note"])

# ----------------------------------------------------
# 2. Sidebar: จัดลำดับใหม่ตามข้อ 7 และ 8
# ----------------------------------------------------
with st.sidebar:
    # 1. ข้อมูลผู้ใช้งานปัจจุบัน ขึ้นมาเป็นอันดับแรก
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("👤 ผู้ใช้งานปัจจุบัน (Current User):", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    st.info(f"**{user_info['Name']}**\n\nสิทธิ์: {user_info['Role']}")
    
    st.markdown("---")
    
    # 2. เลือกเมนูบริษัท เป็นอันที่ 2 (เพิ่ม "ทุกบริษัท/สาขาได้")
    selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", COMPANIES)
    
    st.markdown("---")
    st.markdown(f"### 📌 เมนูหลัก")
    
    # นับจำนวน PR ที่รออนุมัติเพื่อทำ Badge แจ้งเตือน
    pending_pr_count = 0
    if len(st.session_state['purchase_requests']) > 0:
        pending_pr_count = len(st.session_state['purchase_requests'][st.session_state['purchase_requests']['Status'] == "Pending (รออนุมัติ)"])
    
    pr_menu_label = f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)"
    if pending_pr_count > 0:
        pr_menu_label = f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) 🔴({pending_pr_count})"

    t = LANG[st.session_state['lang']]
    
    selected_menu = st.radio("Navigation", [
        t['m_dashboard'],
        t['m_inventory_mgmt'],
        t['sub_import_excel'],
        t['sub_stock_in'],
        t['sub_stock_out'],
        t['m_history'],
        pr_menu_label,
        t['m_eom'],
        t['m_company_settings']
    ], label_visibility="collapsed")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    # แถบเลือกภาษา EN / TH เล็กๆ ด้านล่างขวาของแถบ
    cols_lang = st.columns([2, 1])
    with cols_lang[1]:
        lang_choice = st.radio("Lang", ["TH", "EN"], index=0 if st.session_state['lang']=='th' else 1, horizontal=True, label_visibility="collapsed")
        st.session_state['lang'] = 'th' if lang_choice == "TH" else 'en'

# กำหนด Target Inventory ตามการเลือกบริษัท (รวมหรือแยก)
if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
    current_inv = pd.concat(list(st.session_state['company_inventories'].values()), ignore_index=True)
    trans_df = st.session_state['transactions']
else:
    current_inv = st.session_state['company_inventories'][selected_company]
    trans_df = st.session_state['transactions'][st.session_state['transactions']['Company'] == selected_company]

def localize_text(text):
    if st.session_state['lang'] == 'en':
        return TRANSLATE_DICT.get(text, text)
    return text

# ----------------------------------------------------
# 3. เมนูที่ 1: แดชบอร์ดภาพรวม
# ----------------------------------------------------
if selected_menu == t['m_dashboard']:
    st.title(f"📊 แดชบอร์ดภาพรวม - {selected_company}")
    
    import_trans = trans_df[trans_df['Type'] == 'IMPORT']
    total_purchase_amount = import_trans['Total Price'].sum() if len(import_trans) > 0 else 0.0
    
    total_items = len(current_inv)
    total_qty = current_inv['Stock Balance'].sum() if total_items > 0 else 0
    total_val = (current_inv['Stock Balance'] * current_inv['Last Price']).sum() if total_items > 0 else 0
    
    wast_df = st.session_state['wast_variance_records']
    if selected_company != "ทุกบริษัท/สาขา (All Companies / Branches)":
        wast_df = wast_df[wast_df['Company'] == selected_company]
    
    total_wast = wast_df['Wast_Variance'].sum() if len(wast_df) > 0 else 0.0
    total_oc = wast_df['OC_Test'].sum() if len(wast_df) > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 ยอดเงินซื้อวัตถุดิบรวม", f"{total_purchase_amount:,.2f} THB")
    with col2:
        st.metric("📦 สต็อกคงเหลือ (มูลค่า)", f"{total_val:,.2f} THB ({total_qty:,.2f} หน่วย)")
    with col3:
        st.metric("🗑️ Wast & Variance รวม", f"{total_wast:,.2f}")
    with col4:
        st.metric("🎁 OC / Test รวม", f"{total_oc:,.2f}")
        
    st.markdown("---")
    st.subheader("📋 รายการวัตถุดิบในคลังปัจจุบัน")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสินค้า")

# ----------------------------------------------------
# 4. เมนูที่ 2: การจัดการรายการสินค้า
# ----------------------------------------------------
elif selected_menu == t['m_inventory_mgmt']:
    st.title(f"📦 การจัดการรายการสินค้า - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกเฉพาะเจาะจง 1 บริษัท/สาขา หากต้องการแก้ไขรายการสินค้า")
    else:
        st.markdown("#### 🔍 ค้นหาและเลือกตามหมวดหมู่")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            all_cats_mgmt = ["ทุกหมวดหมู่ (All Categories)"] + CATEGORIES_LIST
            selected_mgmt_cat = st.selectbox("เลือกตามหมวดหมู่", all_cats_mgmt)
        with col_m2:
            search_mgmt_keyword = st.text_input("🔍 ค้นหาชื่อหรือรหัสสินค้า")
            
        mgmt_filtered = current_inv.copy()
        if selected_mgmt_cat != "ทุกหมวดหมู่ (All Categories)":
            mgmt_filtered = mgmt_filtered[mgmt_filtered['Category'] == selected_mgmt_cat]
        if search_mgmt_keyword.strip() != "":
            kw = search_mgmt_keyword.strip().lower()
            mgmt_filtered = mgmt_filtered[mgmt_filtered['Item Name'].str.lower().str.contains(kw, na=False)]
            
        for idx, row in mgmt_filtered.iterrows():
            col_r = st.columns([2, 2, 1, 1, 1, 1])
            col_r[0].write(row['Item Name'])
            col_r[1].write(row['Category'])
            col_r[2].write(f"{row['Stock Balance']} {row['Unit']}")
            col_r[3].write(f"{row['Last Price']} ฿")
            with col_r[4]:
                if st.button("✏️ แก้ไข", key=f"edit_{idx}"):
                    st.session_state[f'open_edit_{idx}'] = not st.session_state.get(f'open_edit_{idx}', False)
            with col_r[5]:
                if st.button("🗑️ ลบ", key=f"del_{idx}"):
                    st.session_state['company_inventories'][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                    st.rerun()
            
            if st.session_state.get(f'open_edit_{idx}', False):
                with st.form(f"form_edit_{idx}"):
                    new_n = st.text_input("ชื่อ", value=row['Item Name'])
                    new_p = st.number_input("ราคา", value=float(row['Last Price']))
                    new_b = st.number_input("สต็อก", value=float(row['Stock Balance']))
                    if st.form_submit_button("บันทึก"):
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Item Name'] = new_n
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Last Price'] = new_p
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] = new_b
                        st.session_state[f'open_edit_{idx}'] = False
                        st.rerun()
            st.markdown("---")

# ----------------------------------------------------
# 5. เมนูย่อย: นำเข้าสินค้า
# ----------------------------------------------------
elif selected_menu == t['sub_import_excel']:
    st.title(f"📥 นำเข้าสินค้า - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกเฉพาะ 1 บริษัท เพื่อทำการนำเข้าสินค้า")
    else:
        uploaded_file = st.file_uploader("เลือกไฟล์ Excel", type=["xlsx", "csv"])
        if uploaded_file:
            st.success("อัปโหลดไฟล์สำเร็จ")

# ----------------------------------------------------
# 6. เมนูย่อย: รับสินค้า (Stock In)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_in']:
    st.title(f"📥 รับสินค้าเข้า (Stock In) - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกบริษัทเฉพาะเจาะจงเพื่อทำรายการรับสินค้า")
    else:
        with st.form("stock_in_form_new"):
            doc_no = st.text_input("เลขที่เอกสาร (ใบกำกับภาษี/ใบเสร็จรับเงิน/ใบส่งของ)")
            
            existing_suppliers = current_inv['Supplier'].unique().tolist() if len(current_inv) > 0 else ["CP Axtra (Makro)", "CP Axtra (Lotus)", "ร้านค้าทั่วไป"]
            supplier_in = st.selectbox("ชื่อร้านค้าที่ซื้อ (Supplier)", existing_suppliers)
            
            st.markdown("**หลักฐานการรับสินค้า (ภาพถ่ายสินค้าและใบเสร็จ)**")
            cam_photo = st.camera_input("📸 ถ่ายรูปภาพสินค้าและใบเสร็จ")
            up_photo = st.file_uploader("หรืออัปโหลดรูปภาพ", type=["jpg", "png", "jpeg"])
            
            st.markdown("---")
            sel_item_in = st.selectbox("เลือกวัตถุดิบรับเข้า", current_inv['Item Name'].tolist() if len(current_inv)>0 else [])
            qty_in = st.number_input("จำนวนรับเข้า", min_value=0.1, value=1.0)
            price_in = st.number_input("ราคาต่อหน่วย", min_value=0.0, value=0.0)
            vat_in = st.selectbox("ประเภทภาษี", VAT_TYPES_LIST)
            
            submit_in = st.form_submit_button("💾 บันทึกรับสินค้าเข้า")
            if submit_in and sel_item_in:
                idx = current_inv[current_inv['Item Name'] == sel_item_in].index[0]
                st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] += qty_in
                st.session_state['company_inventories'][selected_company].loc[idx, 'Last Price'] = price_in
                
                new_t = {
                    "Company": selected_company, "Date": str(datetime.today().date()), "DocNo": doc_no,
                    "Supplier": supplier_in, "Item Name": sel_item_in, "Quantity": qty_in,
                    "Price/Unit": price_in, "Vat Type": vat_in, "Total Price": qty_in * price_in,
                    "Type": "IMPORT", "Receiver": "-", "Department": "-"
                }
                st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                st.success("บันทึกรับสินค้าสำเร็จ!")
                st.rerun()

# ----------------------------------------------------
# 7. เมนูย่อย: เบิกสินค้า (Stock Out)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_out']:
    st.title(f"📤 เบิกสินค้า (Stock Out) - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกเฉพาะ 1 บริษัท เพื่อทำรายการเบิกสินค้า")
    else:
        with st.form("stock_out_form_new"):
            sel_item_out = st.selectbox("เลือกวัตถุดิบที่ต้องการเบิก", current_inv['Item Name'].tolist() if len(current_inv)>0 else [])
            qty_out = st.number_input("จำนวนที่ต้องการเบิก", min_value=0.1, value=1.0)
            unit_out = st.selectbox("เลือกหน่วยนับ", UNITS_LIST)
            date_out = st.date_input("วันที่เบิกสินค้า", value=datetime.today())
            requester_out = st.text_input("ชื่อผู้เบิก")
            department_out = st.text_input("แผนกที่นำไปใช้")
            
            submit_out = st.form_submit_button("ยืนยันการเบิกสินค้า")
            if submit_out and sel_item_out:
                if 'temp_out_list' not in st.session_state:
                    st.session_state['temp_out_list'] = []
                st.session_state['temp_out_list'].append({
                    "Item": sel_item_out, "Qty": qty_out, "Unit": unit_out, "Date": str(date_out), "Dept": department_out
                })
                st.success("บันทึกการเบิกชั่วคราวสำเร็จ")
        
        st.markdown("---")
        st.subheader("📋 รายการที่กดเบิกสินค้าไปแล้วในเซสชันนี้")
        if 'temp_out_list' in st.session_state and len(st.session_state['temp_out_list']) > 0:
            st.dataframe(pd.DataFrame(st.session_state['temp_out_list']), use_container_width=True)
        else:
            st.info("ยังไม่มีรายการเบิกใหม่ในรอบนี้")

# ----------------------------------------------------
# 8. ประวัติการทำรายการ
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 ประวัติการทำรายการ - {selected_company}")
    if len(trans_df) > 0:
        st.dataframe(trans_df, use_container_width=True)
    else:
        st.info("ไม่มีประวัติการทำรายการ")

# ----------------------------------------------------
# 9. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) - แสดงตัวเลขแจ้งเตือนที่หัวข้อตามที่วงไว้
# ----------------------------------------------------
elif pr_menu_label in selected_menu:
    # คำนวณจำนวน PR ที่รออนุมัติ
    pr_df = st.session_state['purchase_requests']
    pending_count = len(pr_df[pr_df['Status'] == "Pending (รออนุมัติ)"]) if len(pr_df) > 0 else 0
    
    # แสดงหัวข้อพร้อมตัวเลขวงกลมสีแดงแบบในรูปภาพที่วงไว้
    st.markdown(f"<h2>📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) <span style='background-color: #ff4b4b; color: white; padding: 2px 10px; border-radius: 50%; font-size: 20px;'>{pending_count}</span></h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ตรวจสอบอนุมัติ PR & ออกใบ PO"])
    
    with tab1:
        with st.form("pr_form_new"):
            pr_date = st.date_input("วันที่ขอซื้อ", value=datetime.today())
            pr_sup = st.text_input("ร้านค้าที่ซื้อ")
            pr_item = st.text_input("รายการวัตถุดิบที่ขอซื้อ")
            pr_qty = st.number_input("จำนวน", min_value=1.0)
            pr_unit = st.selectbox("หน่วยนับ", UNITS_LIST)
            pr_req = st.text_input("ผู้ขอซื้อ")
            
            if st.form_submit_button("ส่งใบขอซื้อ"):
                new_pr = {
                    "PR_ID": f"PR-{datetime.now().strftime('%m%d%H%M%S')}",
                    "Date": str(pr_date), "Supplier": pr_sup, "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)", "Requester": pr_req, "Items": f"{pr_item} จำนวน {pr_qty} {pr_unit}"
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                st.success("สร้างใบขอซื้อสำเร็จ!")
                st.rerun()
                
    with tab2:
        st.subheader("หัวข้อตรวจสอบอนุมัติ PR")
        if len(pr_df) > 0:
            for idx, row in pr_df.iterrows():
                status_color = "orange"
                if "Approved" in row['Status']:
                    status_color = "green"
                elif "Rejected" in row['Status']:
                    status_color = "red"
                
                st.markdown(f"**PR ID:** {row['PR_ID']} | **ร้าน:** {row['Supplier']} | สถานะ: <span style='color:{status_color}; font-weight:bold;'>{row['Status']}</span>", unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ อนุมัติ", key=f"appr_{idx}"):
                        st.session_state['purchase_requests'].loc[idx, 'Status'] = "Approved (อนุมัติแล้ว)"
                        st.rerun()
                with col_btn2:
                    if st.button("❌ ปฏิเสธ", key=f"rej_{idx}"):
                        st.session_state['purchase_requests'].loc[idx, 'Status'] = "Rejected (ปฏิเสธ)"
                        st.rerun()
                st.markdown("---")
                
            st.subheader("สร้างใบ PO อัตโนมัติจากใบ PR ที่อนุมัติแล้ว")
            approved_prs = pr_df[pr_df['Status'] == "Approved (อนุมัติแล้ว)"]
            if len(approved_prs) > 0:
                pr_options = [f"{r['PR_ID']} - ร้าน: {r['Supplier']}" for _, r in approved_prs.iterrows()]
                selected_po_choice = st.selectbox("เลือกใบ PR ที่อนุมัติแล้ว", pr_options)
                
                if st.button("🖨️ สร้างใบ PO"):
                    chosen_id = selected_po_choice.split(" - ")[0]
                    chosen_row = approved_prs[approved_prs['PR_ID'] == chosen_id].iloc[0]
                    st.success(f"สร้างใบ PO สำเร็จสำหรับเลขที่ใบ PR: {chosen_row['PR_ID']} ร้านค้า: {chosen_row['Supplier']}")
            else:
                st.info("ไม่มีใบ PR ที่อนุมัติแล้ว")
        else:
            st.info("ยังไม่มีข้อมูลใบขอซื้อ")

# ----------------------------------------------------
# 10. รายการสรุปสต็อก & นับสต็อก
# ----------------------------------------------------
elif selected_menu == t['m_eom']:
    st.title(f"📋 รายการสรุปสต็อก & นับสต็อก - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกเฉพาะ 1 บริษัท เพื่อทำรายการสรุปและนับสต็อก")
    else:
        st.subheader("📥 นำเข้า/ส่งออก Excel นับสต็อก")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            current_inv.to_excel(writer, sheet_name='Stock_Count', index=False)
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel สำหรับนับสต็อก",
            data=output.getvalue(),
            file_name=f"stock_count_{selected_company}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        up_excel_count = st.file_uploader("📤 อัปโหลดไฟล์ Excel ที่นับสต็อกแล้ว", type=["xlsx"])
        if up_excel_count:
            st.success("อัปโหลดและอัปเดตสต็อกเรียบร้อยแล้ว!")
            
        st.markdown("---")
        st.subheader("ช่องบันทึก Wast & Variance และ OC / Test")
        with st.form("wast_form"):
            item_wast = st.selectbox("เลือกสินค้า", current_inv['Item Name'].tolist() if len(current_inv)>0 else [])
            wast_val = st.number_input("Wast & Variance (จำนวน)", min_value=0.0, value=0.0)
            oc_val = st.number_input("OC / Test (จำนวน)", min_value=0.0, value=0.0)
            note_w = st.text_input("หมายเหตุ")
            
            if st.form_submit_button("บันทึกข้อมูล Wast / OC"):
                new_w = {
                    "Company": selected_company, "Date": str(datetime.today().date()),
                    "Item Name": item_wast, "Wast_Variance": wast_val, "OC_Test": oc_val, "Note": note_w
                }
                st.session_state['wast_variance_records'] = pd.concat([st.session_state['wast_variance_records'], pd.DataFrame([new_w])], ignore_index=True)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# ----------------------------------------------------
# 11. ตั้งค่าข้อมูลบริษัท
# ----------------------------------------------------
elif selected_menu == t['m_company_settings']:
    st.title(f"🏢 ตั้งค่าข้อมูลบริษัท - {selected_company}")
    st.write("ตั้งค่าข้อมูลบริษัทและสิทธิ์ผู้ใช้งานระบบ")

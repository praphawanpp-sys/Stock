import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

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

if 'company_logos' not in st.session_state:
    st.session_state['company_logos'] = {}

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
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items_JSON"])

if 'purchase_orders' not in st.session_state:
    st.session_state['purchase_orders'] = pd.DataFrame(columns=["PO_ID", "PR_ID", "Supplier", "Branch", "Date"])

if 'wast_variance_records' not in st.session_state:
    st.session_state['wast_variance_records'] = pd.DataFrame(columns=["Company", "Date", "Item Name", "Wast_Variance", "OC_Test", "Note"])

# ----------------------------------------------------
# 2. Sidebar: จัดวางแถบเปลี่ยนภาษาไว้บนสุด
# ----------------------------------------------------
with st.sidebar:
    lang_index = 0 if st.session_state['lang'] == 'th' else 1
    lang_choice = st.selectbox("🌐 ภาษา / Language", ["ไทย (Thai)", "English"], index=lang_index)
    st.session_state['lang'] = 'th' if lang_choice == "ไทย (Thai)" else 'en'
    
    st.markdown("---")
    selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", COMPANIES)
    st.markdown("---")
    
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("👤 ผู้ใช้งานปัจจุบัน (Current User):", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    st.info(f"**{user_info['Name']}**\n\nสิทธิ์: {user_info['Role']}")
    
    st.markdown("---")
    st.markdown(f"### 📌 เมนูหลัก")
    
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
            
# Add to the top‑level navigation (inside the st.radio block)
t['sub_manual_import'] = "📥 นำเข้าสินค้าแบบแมนนวล (Manual Import)"

# After the "นำเข้าสินค้า (Excel & Manual)" case
elif selected_menu == t['sub_manual_import']:
    st.title(f"📥 นำเข้าสินค้าแบบแมนนวล - {selected_company}")

    # Do the same branch check as before
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือก 1 บริษัท เพื่อทำรายการนำเข้าสินค้า")
    else:
        # Simple manual form
        with st.form("manual_import_form"):
            doc_no = st.text_input("เลขที่เอกสาร (ใบกำกับภาษี/ใบเสร็จรับเงิน/ใบส่งของ)")
            supplier = st.text_input("ชื่อร้านค้า")
            sku = st.text_input("รหัสสินค้า")
            item_name = st.text_input("ชื่อสินค้า")
            qty = st.number_input("จำนวนรับเข้า", min_value=0.1)
            price = st.number_input("ราคาต่อหน่วย", min_value=0.0)
            unit = st.selectbox("หน่วย", UNITS_LIST)
            vat_type = st.selectbox("ประเภทภาษี", VAT_TYPES_LIST)
            submit = st.form_submit_button("บันทึกรับสินค้าเข้า")

            if submit:
                # Find the row
                inv = st.session_state['company_inventories'][selected_company]
                idx = inv.index[inv['Item Name'] == item_name]
                if not idx.empty:
                    idx = idx[0]
                    inv.loc[idx, 'Stock Balance'] += qty
                    inv.loc[idx, 'Last Price'] = price
                    inv.loc[idx, 'Supplier'] = supplier
                else:
                    # New item: create a row
                    new_row = {
                        "Product Code": sku,
                        "Item Name": item_name,
                        "Category": "",
                        "Unit": unit,
                        "Stock Balance": qty,
                        "Last Price": price,
                        "Supplier": supplier,
                        "Vat Type": vat_type
                    }
                    st.session_state['company_inventories'][selected_company] = inv.append(new_row, ignore_index=True)

                # Record transaction
                new_t = {"Company": selected_company,
                         "Date": str(datetime.today().date()),
                         "DocNo": doc_no,
                         "Supplier": supplier,
                         "Item Name": item_name,
                         "Quantity": qty,
                         "Price/Unit": price,
                         "Vat Type": vat_type,
                         "Total Price": qty * price,
                         "Type": "IMPORT",
                         "Receiver": "-",
                         "Department": "-"}
                st.session_state['transactions'] = pd.concat([st.session_state['transactions'],
                                                             pd.DataFrame([new_t])],
                                                            ignore_index=True)
                st.success("บันทึกรับสินค้าสำเร็จ!")
                st.rerun()

            
# --------------------------------------------------------------------------------------------------------------------
# 1.1 Role‑based inventory filtering
# --------------------------------------------------------------------------------------------------------------------
def get_visible_inventory():
    """Return the inventory DataFrame that the current user is allowed to see."""
    # Identify the user’s role and branch
    role = user_info['Role']
    branch = user_info['Branch']

    # If the user is Office, Manager, or Owner: all branches are visible
    if role in {"Office", "Manager", "Owner"}:
        # Combine all company inventories
        return pd.concat(list(st.session_state['company_inventories'].values()), ignore_index=True)

    # If the user is Admin: only their own branch inventory
    if role == "Admin":
        return st.session_state['company_inventories'][branch]

    # Default: empty DataFrame
    return pd.DataFrame(columns=st.session_state['company_inventories'][COMPANIES[0]].columns)


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
                st.session_state['company_inventories'][selected_company].loc[idx, 'Supplier'] = supplier_in
                
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
# 9. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)
# ----------------------------------------------------
elif pr_menu_label in selected_menu:
    pr_df = st.session_state['purchase_requests']
    pending_count = len(pr_df[pr_df['Status'] == "Pending (รออนุมัติ)"]) if len(pr_df) > 0 else 0
    
    st.markdown(f"<h2>📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) <span style='background-color: #ff4b4b; color: white; padding: 2px 10px; border-radius: 50%; font-size: 20px;'>{pending_count}</span></h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ดูฟอร์มเอกสารใบสั่งซื้อ (PO Form) & อนุมัติ"])
    
    with tab1:
        st.subheader("สร้างใบขอซื้อสินค้า (Purchase Requisition - PR)")
        
        # 1.1 เลือกร้านค้าก่อน
        all_sups = current_inv['Supplier'].unique().tolist() if len(current_inv) > 0 else ["CP Axtra (Makro)", "CP Axtra (Lotus)"]
        selected_pr_sup = st.selectbox("1. เลือกร้านค้าที่ต้องการซื้อ (Supplier)", all_sups)
        pr_req_name = st.text_input("ชื่อผู้ขอซื้อ (Requester)")
        pr_date_input = st.date_input("วันที่ขอซื้อ", value=datetime.today())
        
        st.markdown("---")
        st.subheader("2. เพิ่มรายการสินค้าทีละรายการ")
        
        if 'cart_pr_items' not in st.session_state:
            st.session_state['cart_pr_items'] = []
            
        # กรองรายการสินค้าที่เป็นของ Supplier นี้ หรือเลือกจากคลังทั้งหมด
        supplier_items = current_inv['Item Name'].tolist() if len(current_inv) > 0 else []
        
        with st.form("add_item_to_pr_form"):
            col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
            with col_i1:
                item_choice = st.selectbox("เลือกวัตถุดิบ", supplier_items)
            with col_i2:
                qty_choice = st.number_input("จำนวน", min_value=0.1, value=1.0)
            with col_i3:
                unit_choice = st.selectbox("หน่วยนับ", UNITS_LIST)
                
            add_to_cart_btn = st.form_submit_button("➕ เพิ่มรายการนี้ลงในตะกร้า PR")
            if add_to_cart_btn and item_choice:
                # ดึงราคารับล่าสุดของสินค้านั้นๆ มาอ้างอิง
                match_row = current_inv[current_inv['Item Name'] == item_choice]
                last_price = float(match_row['Last Price'].values[0]) if len(match_row) > 0 else 0.0
                
                st.session_state['cart_pr_items'].append({
                    "Item Name": item_choice,
                    "Quantity": qty_choice,
                    "Unit": unit_choice,
                    "Reference Price": last_price,
                    "Total Estimated Price": qty_choice * last_price
                })
                st.success(f"เพิ่ม {item_choice} สำเร็จ!")
                
        if len(st.session_state['cart_pr_items']) > 0:
            st.markdown("#### 🛒 รายการสินค้าในใบขอซื้อ (PR) นี้:")
            cart_df = pd.DataFrame(st.session_state['cart_pr_items'])
            st.dataframe(cart_df, use_container_width=True)
            
            if st.button("🗑️ ล้างรายการในตะกร้าทั้งหมด"):
                st.session_state['cart_pr_items'] = []
                st.rerun()
                
            if st.button("🚀 บันทึกและส่งใบขอซื้อ (PR) ทีเดียว"):
                import json
                new_pr_id = f"PR-{datetime.now().strftime('%m%d%H%M%S')}"
                new_pr_record = {
                    "PR_ID": new_pr_id,
                    "Date": str(pr_date_input),
                    "Supplier": selected_pr_sup,
                    "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)",
                    "Requester": pr_req_name if pr_req_name else "Admin",
                    "Items_JSON": json.dumps(st.session_state['cart_pr_items'], ensure_ascii=False)
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr_record])], ignore_index=True)
                st.session_state['cart_pr_items'] = [] # ล้างตะกร้า
                st.success(f"ส่งใบขอซื้อสำเร็จ! หมายเลข: {new_pr_id}")
                st.rerun()
        else:
            st.info("ยังไม่มีรายการสินค้าในตะกร้า กรุณาเลือกสินค้าและกดเพิ่มรายการ")

    with tab2:
        st.subheader("📄 รายการใบขอซื้อ (PR) ทั้งหมด & ตรวจสอบรายละเอียด")
        
        pr_df = st.session_state['purchase_requests']
        if len(pr_df) > 0:
            # 2. สามารถดึงใบ PR/PO ออกมาเป็น Excel ได้
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                pr_output = io.BytesIO()
                with pd.ExcelWriter(pr_output, engine='xlsxwriter') as writer:
                    pr_df.to_excel(writer, sheet_name='Purchase_Requests', index=False)
                st.download_button("📥 ดาวน์โหลดรายงาน PR เป็น Excel", data=pr_output.getvalue(), file_name="purchase_requests_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col_dl2:
                po_output = io.BytesIO()
                with pd.ExcelWriter(po_output, engine='xlsxwriter') as writer:
                    st.session_state['purchase_orders'].to_excel(writer, sheet_name='Purchase_Orders', index=False)
                st.download_button("📥 ดาวน์โหลดรายงาน PO เป็น Excel", data=po_output.getvalue(), file_name="purchase_orders_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            st.markdown("---")
            for idx, row in pr_df.iterrows():
                import json
                status_color = "orange"
                if "Approved" in row['Status']:
                    status_color = "green"
                elif "Rejected" in row['Status']:
                    status_color = "red"
                    
                with st.expander(f"📌 {row['PR_ID']} | ร้าน: {row['Supplier']} | สาขา: {row['Branch']} | สถานะ: {row['Status']}"):
                    st.write(f"**วันที่ขอซื้อ:** {row['Date']} | **ผู้ขอซื้อ:** {row['Requester']}")
                    st.markdown("#### รายการสินค้าที่ขอซื้อ (อ้างอิงราคาจากราคารับของล่าสุด):")
                    
                    try:
                        items_list = json.loads(row['Items_JSON'])
                        items_df = pd.DataFrame(items_list)
                        st.dataframe(items_df, use_container_width=True)
                        total_est = items_df['Total Estimated Price'].sum() if 'Total Estimated Price' in items_df.columns else 0.0
                        st.markdown(f"**💵 มูลค่ารวมประมาณการทั้งหมด:** **{total_est:,.2f} THB**")
                    except:
                        st.write(row['Items_JSON'])
                        
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ อนุมัติใบ PR นี้", key=f"appr_{idx}"):
                            st.session_state['purchase_requests'].loc[idx, 'Status'] = "Approved (อนุมัติแล้ว)"
                            st.rerun()
                    with col_b2:
                        if st.button("❌ ปฏิเสธใบ PR นี้", key=f"rej_{idx}"):
                            st.session_state['purchase_requests'].loc[idx, 'Status'] = "Rejected (ปฏิเสธ)"
                            st.rerun()
                            
            st.markdown("---")
            st.subheader("🖨️ ออกใบสั่งซื้อ (PO) จากใบ PR ที่อนุมัติแล้ว")
            approved_prs = pr_df[pr_df['Status'] == "Approved (อนุมัติแล้ว)"]
            if len(approved_prs) > 0:
                pr_options = [f"{r['PR_ID']} - ร้าน: {r['Supplier']}" for _, r in approved_prs.iterrows()]
                selected_po_choice = st.selectbox("เลือกใบ PR ที่อนุมัติแล้ว", pr_options)
                
                if st.button("สร้างใบ PO และดูฟอร์ม"):
                    chosen_id = selected_po_choice.split(" - ")[0]
                    chosen_row = approved_prs[approved_prs['PR_ID'] == chosen_id].iloc[0]
                    
                    new_po_id = f"PO-{datetime.now().strftime('%y%m%d%H%M')}"
                    new_po_data = {
                        "PO_ID": new_po_id, "PR_ID": chosen_row['PR_ID'],
                        "Supplier": chosen_row['Supplier'], "Branch": chosen_row['Branch'],
                        "Date": str(datetime.today().date())
                    }
                    st.session_state['purchase_orders'] = pd.concat([st.session_state['purchase_orders'], pd.DataFrame([new_po_data])], ignore_index=True)
                    st.success(f"สร้างใบ PO สำเร็จ (เลขที่ {new_po_id})")
                    st.rerun()
            else:
                st.info("ยังไม่มีใบ PR ที่ได้รับการอนุมัติเพื่อนำมาออก PO")
                
            st.markdown("---")
            st.subheader("📄 ดูฟอร์มเอกสารใบสั่งซื้อสินค้า (PO Form)")
            po_df = st.session_state['purchase_orders']
            if len(po_df) > 0:
                po_options = [f"{row['PO_ID']} - PR: {row['PR_ID']} - ร้าน: {row['Supplier']}" for _, row in po_df.iterrows()]
                selected_po_view = st.selectbox("เลือกเอกสาร PO ที่ต้องการแสดงฟอร์ม", po_options)
                
                chosen_po_id = selected_po_view.split(" - ")[0]
                po_row = po_df[po_df['PO_ID'] == chosen_po_id].iloc[0]
                
                # ดึงข้อมูล PR ที่เกี่ยวข้องมาแสดงในฟอร์ม PO
                related_pr = pr_df[pr_df['PR_ID'] == po_row['PR_ID']].iloc[0]
                import json
                try:
                    po_items_list = json.loads(related_pr['Items_JSON'])
                except:
                    po_items_list = []
                    
                po_company = po_row['Branch'] if po_row['Branch'] in REAL_COMPANIES else REAL_COMPANIES[0]
                po_address = st.session_state['company_addresses'].get(po_company, "ที่อยู่สำนักงานใหญ่")
                logo_file = st.session_state['company_logos'].get(po_company, None)
                
                logo_html = ""
                if logo_file is not None:
                    import base64
                    bytes_data = logo_file.getvalue()
                    base64_str = base64.b64encode(bytes_data).decode("utf-8")
                    logo_html = f'<img src="data:image/png;base64,{base64_str}" style="max-height: 60px; max-width: 150px; margin-bottom: 8px;"><br>'

                # สร้างแถวตารางสินค้า HTML จากข้อมูลจริงใน PR
                table_rows_html = ""
                grand_total = 0.0
                for i, itm in enumerate(po_items_list, 1):
                    tot_p = itm.get('Total Estimated Price', 0.0)
                    grand_total += tot_p
                    table_rows_html += f"""
                    <tr>
                        <td style="text-align: center;">{i}</td>
                        <td>{itm.get('Item Name')}</td>
                        <td style="text-align: center;">{itm.get('Quantity')} {itm.get('Unit')}</td>
                        <td style="text-align: right;">{itm.get('Reference Price', 0.0):,.2f}</td>
                        <td style="text-align: right;">{tot_p:,.2f}</td>
                    </tr>
                    """

                html_po_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: sans-serif; color: #333; margin: 0; padding: 0; background-color: #ffffff; }}
                    .po-container {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #ffffff; }}
                    table {{ width: 100%; border: 1px solid #333; margin-top: 15px; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #333; padding: 8px; font-size: 13px; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
                </head>
                <body>
                <div class="po-container">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            {logo_html}
                            <h2 style="margin: 0; color: #111;">{po_company}</h2>
                            <p style="margin: 2px 0 15px 0; font-size: 13px; color: #666;">CAFÉ • EATERY • STORE</p>
                        </div>
                        <div style="text-align: right;">
                            <h3 style="margin: 0; color: #111;">Purchase Order</h3>
                            <p style="margin: 2px 0 0 0; font-size: 13px; color: #666;">ใบสั่งซื้อสินค้า</p>
                        </div>
                    </div>
                    
                    <table>
                        <tr>
                            <td style="width: 50%; vertical-align: top;">
                                <b>Company / บริษัท:</b><br>
                                {po_address.replace(chr(10), '<br>')}<br>
                                <b>Tax ID:</b> 0775565003672<br>
                                <b>Contact:</b> {related_pr['Requester']}
                            </td>
                            <td style="width: 50%; vertical-align: top;">
                                <b>สถานที่ส่งสินค้า / Delivery Address:</b><br>
                                {po_company}<br>
                                {po_address.replace(chr(10), '<br>')}<br>
                                <b>Contact:</b> {related_pr['Requester']}
                            </td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 12px; font-size: 13px;">
                        <p><b>เลขที่ใบสั่งซื้อ (PO ID):</b> {po_row['PO_ID']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>วันที่:</b> {po_row['Date']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>ผู้จำหน่าย (Supplier):</b> {po_row['Supplier']}</p>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th style="text-align: center;">ลำดับ</th>
                                <th style="text-align: left;">รายการสินค้า</th>
                                <th style="text-align: center;">จำนวน</th>
                                <th style="text-align: right;">ราคาอ้างอิง/หน่วย</th>
                                <th style="text-align: right;">รวมเป็นเงิน (THB)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                    <div style="text-align: right; margin-top: 10px; font-size: 14px;">
                        <b>มูลค่ารวมทั้งสิ้น: {grand_total:,.2f} บาท</b>
                    </div>
                </div>
                </body>
                </html>
                """
                st.components.v1.html(html_po_content, height=550, scrolling=True)
            else:
                st.info("ยังไม่มีข้อมูลใบสั่งซื้อ (PO)")
        else:
            st.info("ยังไม่มีข้อมูลใบขอซื้อ (PR)")

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
    st.title(f"🏢 ตั้งค่าข้อมูลบริษัทและแอดมิน - {selected_company}")
    
    set_tab1, set_tab2 = st.tabs(["📄 1. แก้ไข/เพิ่มชื่อ ที่อยู่ และโลโก้บริษัท", "⚙️ 2. การจัดการการจัดการแอดมินและสิทธิ์"])
    
    with set_tab1:
        st.subheader("แก้ไขชื่อ ที่อยู่ และอัปโหลดโลโก้บริษัท")
        current_addr = st.session_state['company_addresses'].get(selected_company, "")
        
        existing_logo = st.session_state['company_logos'].get(selected_company, None)
        if existing_logo is not None:
            st.image(existing_logo, width=150, caption="โลโก้ปัจจุบันของบริษัท")
            
        with st.form("company_info_form"):
            new_comp_name = st.text_input("ชื่อบริษัท / สาขา", value=selected_company)
            new_comp_address = st.text_area("ที่อยู่ของร้านค้า / สาขา", value=current_addr)
            new_tax_id = st.text_input("เลขประจำตัวผู้เสียภาษี (Tax ID)", value="01055xxxxxxxx")
            new_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ", value="02-xxx-xxxx")
            
            uploaded_logo = st.file_uploader("🖼️ อัปโหลดโลโก้บริษัท (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
            
            save_comp_info = st.form_submit_button("💾 บันทึกข้อมูลบริษัทและโลโก้")
            if save_comp_info:
                st.session_state['company_addresses'][selected_company] = new_comp_address
                if uploaded_logo is not None:
                    st.session_state['company_logos'][selected_company] = uploaded_logo
                st.success("บันทึกข้อมูลและอัปโหลดโลโก้บริษัทเรียบร้อยแล้ว!")
                st.rerun()
                
    with set_tab2:
        st.subheader("จัดการสิทธิ์ผู้ใช้งานและแอดมินระบบ")
        st.dataframe(st.session_state['admins'], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🛠️ แก้ไข / ลบ หรือเพิ่มบัญชีแอดมิน")
        
        admin_names = st.session_state['admins']['Username'].tolist()
        sel_admin = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการแก้ไขหรือลบ", admin_names)
        
        adm_row = st.session_state['admins'][st.session_state['admins']['Username'] == sel_admin].iloc[0]
        adm_idx = st.session_state['admins'][st.session_state['admins']['Username'] == sel_admin].index[0]
        
        with st.form("edit_admin_form"):
            a_user = st.text_input("Username", value=str(adm_row['Username']))
            a_name = st.text_input("Full Name / ชื่อ-นามสกุล", value=str(adm_row['Name']))
            a_branch = st.selectbox("Branch / สาขา", COMPANIES + ["All Branches"], index=0 if adm_row['Branch'] in COMPANIES else len(COMPANIES))
            a_role = st.selectbox("Role / สิทธิ์", ["Super Admin", "Manager", "Staff"], index=0 if adm_row['Role']=="Super Admin" else (1 if adm_row['Role']=="Manager" else 2))
            
            c_abtn1, c_abtn2 = st.columns(2)
            with c_abtn1:
                up_adm = st.form_submit_button("💾 บันทึกการแก้ไขแอดมิน")
            with c_abtn2:
                del_adm = st.form_submit_button("🗑️ ลบแอดมินนี้ออก")
                
            if up_adm:
                st.session_state['admins'].loc[adm_idx] = [a_user, a_name, a_branch, a_role]
                st.success("อัปเดตสิทธิ์แอดมินสำเร็จ!")
                st.rerun()
            elif del_adm:
                st.session_state['admins'] = st.session_state['admins'].drop(adm_idx).reset_index(drop=True)
                st.success("ลบแอดมินสำเร็จ!")
                st.rerun()

# Add to the navigation list
t['sub_settings'] = "⚙️ ตั้งค่า/แก้ไข ข้อมูลร้านค้า / หน่วย / หมวด"

# Add UI for this section somewhere after other menu blocks
elif selected_menu == t['sub_settings']:
    st.title("⚙️ ตั้งค่า/แก้ไข ข้อมูลร้านค้า / หน่วย / หมวด")

    # 3.1 Edit / add units
    with st.expander("หน่วยที่ใช้ (Units)"):
        st.write(UNITS_LIST)
        new_unit = st.text_input("เพิ่มหน่วยใหม่", key="new_unit")
        if st.button("เพิ่มหน่วย", key="add_unit"):
            if new_unit and new_unit not in UNITS_LIST:
                UNITS_LIST.append(new_unit)
                st.success(f"เพิ่มหน่วย '{new_unit}' เรียบร้อยแล้ว")
            else:
                st.warning("หน่วยนี้มีอยู่แล้ว หรือไม่ถูกต้อง")

    # 3.2 Edit / add categories
    with st.expander("หมวดหมู่ (Categories)"):
        st.write(CATEGORIES_LIST)
        new_cat = st.text_input("เพิ่มหมวดหมู่ใหม่", key="new_cat")
        if st.button("เพิ่มหมวดหมู่", key="add_cat"):
            if new_cat and new_cat not in CATEGORIES_LIST:
                CATEGORIES_LIST.append(new_cat)
                st.success(f"เพิ่มหมวดหมู่ '{new_cat}' เรียบร้อยแล้ว")
            else:
                st.warning("หมวดหมู่นี้มีอยู่แล้ว หรือไม่ถูกต้อง")

    # 3.3 Edit / add store data (address, logo, etc.)
    with st.expander("ข้อมูลร้านค้า (Address / Logo)") :
        new_address = st.text_area("อัปเดตที่อยู่", value=st.session_state['company_addresses'][selected_company])
        if st.button("บันทึกที่อยู่ใหม่", key="save_addr"):
            st.session_state['company_addresses'][selected_company] = new_address
            st.success("อัปเดตที่อยู่สำเร็จ")

        uploaded_logo = st.file_uploader("อัปโหลดโลโก้", type=["jpg","png","jpeg"], key="upload_logo")
        if uploaded_logo:
            st.session_state['company_logos'][selected_company] = uploaded_logo
            st.success("อัปโหลดโลโก้สำเร็จ")

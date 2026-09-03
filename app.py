import streamlit as st
import pandas as pd
from datetime import datetime

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
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)"
]

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
        "sidebar_lang": "🌐 เลือกภาษา / Language",
        "sidebar_company": "🏢 เลือกบริษัท / สาขา",
        "sidebar_user": "👤 ผู้ใช้งานปัจจุบัน",
        "role_label": "สิทธิ์:",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory_mgmt": "📦 การจัดการรายการสินค้า",
        "sub_import_excel": "📥 นำเข้าสินค้า (Excel & Manual)",
        "sub_stock_in": "📥 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อกสิ้นเดือน",
        "m_company_settings": "🏢 ตั้งค่าข้อมูลบริษัท",
    },
    "en": {
        "title": "Enterprise Food Cost & Stock Management System",
        "sidebar_lang": "🌐 Select Language / ภาษา",
        "sidebar_company": "🏢 Select Company / Branch",
        "sidebar_user": "👤 Current User",
        "role_label": "Role:",
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
    st.session_state['company_addresses'] = {comp: f"ที่อยู่สำนักงานใหญ่/สาขา ของ {comp} (กรุณากรอกข้อมูลที่อยู่)" for comp in COMPANIES}

if 'company_inventories' not in st.session_state:
    st.session_state['company_inventories'] = {}
    for comp in COMPANIES:
        st.session_state['company_inventories'][comp] = pd.DataFrame(columns=[
            "Product Code", "Item Name", "Category", "Unit", "Stock Balance", "Last Price", "Supplier", "Vat Type"
        ])
    st.session_state['company_inventories'][COMPANIES[0]] = pd.DataFrame([
        {"Product Code": "422582", "Item Name": "นมจืด 1 ลิตร", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Box", "Stock Balance": 25.0, "Last Price": 109.0, "Supplier": "CP Axtra (Makro)", "Vat Type": "Non Vat"},
        {"Product Code": "2502009877754", "Item Name": "กระเทียมดัดจุก 500 ก.", "Category": "ผักและผลไม้ / Vegetables & Fruits", "Unit": "Pack", "Stock Balance": 10.0, "Last Price": 40.0, "Supplier": "CP Axtra (Lotus)", "Vat Type": "Non Vat"},
        {"Product Code": "54061057", "Item Name": "คิทแคท ทริกเกอร์ 500 กรัม", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Bag", "Stock Balance": 0.0, "Last Price": 130.0, "Supplier": "กส-สรา ค้าส่ง", "Vat Type": "Vat 7%"}
    ])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame([
        {"Company": COMPANIES[0], "Date": str(datetime.today().date()), "DocNo": "INV-001", "Supplier": "CP Axtra (Makro)", "Item Name": "นมจืด 1 ลิตร", "Quantity": 25.0, "Price/Unit": 109.0, "Vat Type": "Non Vat", "Total Price": 2725.0, "Type": "IMPORT", "Receiver": "-", "Department": "-"}
    ])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": COMPANIES[0], "Role": "Manager"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items"])

# ----------------------------------------------------
# 2. Sidebar: เลือกภาษา บริษัท และผู้ใช้งาน (จัดลำดับเมนูใหม่ตามข้อ 2 และข้อ 8)
# ----------------------------------------------------
with st.sidebar:
    selected_lang_label = st.selectbox("🌐 Language / ภาษา", ["ไทย (Thai)", "English"], index=0 if st.session_state['lang']=='th' else 1)
    st.session_state['lang'] = 'th' if "Thai" in selected_lang_label else 'en'
    t = LANG[st.session_state['lang']]
    
    st.markdown("---")
    selected_company = st.selectbox(f"🏢 {t['sidebar_company']}", COMPANIES)
    
    st.markdown("---")
    st.markdown(f"**{t['sidebar_user']}**")
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("Switch User:", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    st.info(f"**{user_info['Name']}**\n\n{t['role_label']} {user_info['Role']}")
    
    st.markdown("---")
    st.markdown(f"### {t['menu']}")
    
    # จัดลำดับเมนูให้ "ตั้งค่าข้อมูลบริษัท" อยู่เป็นเมนูที่ 2 นับจากท้ายสุด
    selected_menu = st.radio("Navigation", [
        t['m_dashboard'],
        t['m_inventory_mgmt'],
        t['sub_import_excel'],
        t['sub_stock_in'],
        t['sub_stock_out'],
        t['m_history'],
        t['m_pr_po'],
        t['m_eom'],
        t['m_company_settings']
    ], label_visibility="collapsed")

current_inv = st.session_state['company_inventories'][selected_company]
trans_df = st.session_state['transactions']

def localize_text(text):
    if st.session_state['lang'] == 'en':
        return TRANSLATE_DICT.get(text, text)
    return text

# ----------------------------------------------------
# 3. เมนูที่ 1: แดชบอร์ดภาพรวม
# ----------------------------------------------------
if selected_menu == t['m_dashboard']:
    st.title(f"📊 {t['m_dashboard']} - {selected_company}")
    
    st.markdown("#### 🔍 ตัวกรองข้อมูล (Filters)")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        suppliers_list = ["All Suppliers / ทุกร้านค้า"] + (current_inv['Supplier'].unique().tolist() if len(current_inv)>0 else [])
        selected_supplier_filter = st.selectbox("Supplier / ร้านค้าที่ซื้อ", suppliers_list, key="dash_sup_filter")
    with col_f2:
        start_date = st.date_input("Start Date / ตั้งแต่วันที่", value=datetime.today().replace(day=1))
    with col_f3:
        end_date = st.date_input("End Date / ถึงวันที่", value=datetime.today())
        
    st.markdown("---")
    
    filtered_inv = current_inv.copy()
    if selected_supplier_filter != "All Suppliers / ทุกร้านค้า":
        filtered_inv = filtered_inv[filtered_inv['Supplier'] == selected_supplier_filter]

    total_items = len(filtered_inv)
    total_qty = filtered_inv['Stock Balance'].sum() if total_items > 0 else 0
    total_val = (filtered_inv['Stock Balance'] * filtered_inv['Last Price']).sum() if total_items > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items / จำนวนรายการวัตถุดิบ", f"{total_items} Items")
    with col2:
        st.metric("Total Stock Balance / สต็อกคงเหลือรวม", f"{total_qty:,.2f}")
    with col3:
        st.metric("Estimated Stock Value / มูลค่าสต็อกรวม", f"{total_val:,.2f} THB")
        
    st.subheader("📦 Inventory Data Table / ตารางข้อมูลวัตถุดิบ")
    if len(filtered_inv) > 0:
        display_inv = filtered_inv.copy()
        if st.session_state['lang'] == 'en':
            display_inv['Category'] = display_inv['Category'].apply(localize_text)
        st.dataframe(display_inv, use_container_width=True)
    else:
        st.info("No inventory data found for this selection.")

# ----------------------------------------------------
# 4. เมนูที่ 2: การจัดการรายการสินค้า (เพิ่มหัวข้อเลือกตามหมวดหมู่ + แก้ไขใต้รายการนั้น)
# ----------------------------------------------------
elif selected_menu == t['m_inventory_mgmt']:
    st.title(f"📦 {t['m_inventory_mgmt']} - {selected_company}")
    
    st.markdown("#### 🔍 ค้นหาและกรองข้อมูลสินค้า")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        all_suppliers_mgmt = ["ทั้งหมดทุกร้านค้า (All Suppliers)"] + (current_inv['Supplier'].unique().tolist() if len(current_inv)>0 else [])
        selected_mgmt_supplier = st.selectbox("เลือกตามร้านค้าที่ซื้อ (Select Supplier)", all_suppliers_mgmt)
    with col_m2:
        # เพิ่มหัวข้อ "เลือกตามหมวดหมู่"
        all_cats_mgmt = ["ทุกหมวดหมู่ (All Categories)"] + CATEGORIES_LIST
        selected_mgmt_cat = st.selectbox("เลือกตามหมวดหมู่ (Select Category)", all_cats_mgmt)
    with col_m3:
        search_mgmt_keyword = st.text_input("🔍 ค้นหาด้วยชื่อสินค้า หรือ รหัสสินค้า")
        
    st.markdown("---")
    
    mgmt_filtered = current_inv.copy()
    if selected_mgmt_supplier != "ทั้งหมดทุกร้านค้า (All Suppliers)":
        mgmt_filtered = mgmt_filtered[mgmt_filtered['Supplier'] == selected_mgmt_supplier]
    if selected_mgmt_cat != "ทุกหมวดหมู่ (All Categories)":
        mgmt_filtered = mgmt_filtered[mgmt_filtered['Category'] == selected_mgmt_cat]
    if search_mgmt_keyword.strip() != "":
        kw = search_mgmt_keyword.strip().lower()
        mgmt_filtered = mgmt_filtered[
            mgmt_filtered['Item Name'].str.lower().str.contains(kw, na=False) |
            mgmt_filtered['Product Code'].str.lower().str.contains(kw, na=False)
        ]
        
    st.subheader(f"📋 รายการสินค้าทั้งหมด ({len(mgmt_filtered)} รายการ)")
    
    if len(mgmt_filtered) > 0:
        h_col = st.columns([1.2, 2.2, 2.2, 1, 0.8, 0.8, 1.5, 1, 1.2])
        headers = ["Product Code", "Item Name", "Category", "Unit", "Stock", "Price", "Supplier", "Vat Type", "จัดการ"]
        for hc, h_text in zip(h_col, headers):
            hc.markdown(f"**{h_text}**")
        st.markdown("---")
        
        for idx, row in mgmt_filtered.iterrows():
            r_col = st.columns([1.2, 2.2, 2.2, 1, 0.8, 0.8, 1.5, 1, 0.5, 0.5])
            
            r_col[0].write(str(row['Product Code']))
            r_col[1].write(str(row['Item Name']))
            r_col[2].write(str(row['Category']))
            r_col[3].write(str(row['Unit']))
            r_col[4].write(str(row['Stock Balance']))
            r_col[5].write(str(row['Last Price']))
            r_col[6].write(str(row['Supplier']))
            r_col[7].write(str(row.get('Vat Type', 'Non Vat')))
            
            with r_col[8]:
                if st.button("✏️", key=f"edit_btn_{idx}", help="แก้ไขรายการนี้"):
                    # สลับสถานะเปิด/ปิดฟอร์มแก้ไขเฉพาะแถวนี้
                    current_state = st.session_state.get(f'edit_open_{selected_company}_{idx}', False)
                    st.session_state[f'edit_open_{selected_company}_{idx}'] = not current_state
            with r_col[9]:
                if st.button("🗑️", key=f"del_btn_{idx}", help="ลบรายการนี้"):
                    st.session_state['company_inventories'][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                    st.success(f"ลบรายการ {row['Item Name']} สำเร็จ!")
                    st.rerun()
            
            # ถ้าเปิดแก้ไข ให้แสดงฟอร์มแทรกขึ้นมาใต้บรรทัดนั้นทันที
            if st.session_state.get(f'edit_open_{selected_company}_{idx}', False):
                with st.container():
                    st.markdown(f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #ff4b4b;'>", unsafe_allow_html=True)
                    st.write(f"🛠️ **กำลังแก้ไขรายการ: {row['Item Name']}**")
                    existing_suppliers = current_inv['Supplier'].unique().tolist()
                    if not existing_suppliers:
                        existing_suppliers = ["General", "CP Axtra (Makro)", "CP Axtra (Lotus)"]

                    with st.form(f"inline_edit_form_{idx}"):
                        e_code = st.text_input("รหัสสินค้า (Product Code)", value=str(row['Product Code']))
                        e_name = st.text_input("ชื่อวัตถุดิบ (Item Name)", value=str(row['Item Name']))
                        
                        curr_cat = str(row['Category'])
                        cat_idx = CATEGORIES_LIST.index(curr_cat) if curr_cat in CATEGORIES_LIST else 0
                        e_cat = st.selectbox("หมวดหมู่ (Category)", CATEGORIES_LIST, index=cat_idx)
                        
                        curr_unit = str(row['Unit'])
                        unit_idx = UNITS_LIST.index(curr_unit) if curr_unit in UNITS_LIST else 0
                        e_unit = st.selectbox("หน่วยนับ (Unit)", UNITS_LIST, index=unit_idx)
                        
                        e_bal = st.number_input("จำนวนสต็อก (Stock Balance)", value=float(row['Stock Balance']))
                        e_price = st.number_input("ราคาล่าสุด (Last Price)", value=float(row['Last Price']))
                        
                        curr_sup = str(row['Supplier'])
                        sup_idx = existing_suppliers.index(curr_sup) if curr_sup in existing_suppliers else 0
                        e_sup = st.selectbox("ร้านค้าที่ซื้อ (Supplier)", existing_suppliers, index=sup_idx)
                        
                        curr_vat = str(row.get('Vat Type', 'Non Vat'))
                        vat_idx = VAT_TYPES_LIST.index(curr_vat) if curr_vat in VAT_TYPES_LIST else 0
                        e_vat = st.selectbox("ประเภทภาษี (Vat Type)", VAT_TYPES_LIST, index=vat_idx)
                        
                        col_sub1, col_sub2 = st.columns(2)
                        with col_sub1:
                            save_edit = st.form_submit_button("💾 บันทึกการแก้ไข")
                        with col_sub2:
                            cancel_edit = st.form_submit_button("❌ ยกเลิก")
                            
                        if save_edit:
                            st.session_state['company_inventories'][selected_company].loc[idx] = [e_code, e_name, e_cat, e_unit, e_bal, e_price, e_sup, e_vat]
                            st.session_state[f'edit_open_{selected_company}_{idx}'] = False
                            st.success("บันทึกการแก้ไขสำเร็จ!")
                            st.rerun()
                        elif cancel_edit:
                            st.session_state[f'edit_open_{selected_company}_{idx}'] = False
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("ไม่พบรายการสินค้าตามเงื่อนไขที่เลือก")

# ----------------------------------------------------
# 5. เมนูย่อย: นำเข้าสินค้า (Excel Import & Manual Add)
# ----------------------------------------------------
elif selected_menu == t['sub_import_excel']:
    st.title(f"📥 {t['sub_import_excel']} - {selected_company}")
    
    tab_m1, tab_m2 = st.tabs(["📁 นำเข้าผ่านไฟล์ Excel (Excel Import)", "✍️ เพิ่มสินค้าแบบแมนนวล (Manual Add)"])
    
    with tab_m1:
        st.write("รูปแบบไฟล์: คอลัมน์ 0=Supplier, คอลัมน์ 1=รหัสสินค้า, คอลัมน์ 2=ชื่อวัตถุดิบ, คอลัมน์ 3=ราคา, คอลัมน์ 4=หน่วยนับ")
        uploaded_file = st.file_uploader("เลือกไฟล์ Excel / Choose Excel File", type=["xlsx", "xls", "csv"])
        
        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file, header=None)
                st.write(f"พบข้อมูลทั้งหมด: {len(df_raw)} แถว (แสดงตัวอย่าง 5 แถวแรก):")
                st.dataframe(df_raw.head())
                
                if st.button("ยืนยันการนำเข้าข้อมูลเข้าสู่ระบบ / Confirm Excel Import"):
                    new_items_list = []
                    for index, row in df_raw.iloc[1:].iterrows():
                        supplier = str(row.get(0, "General"))
                        p_code = str(row.get(1, "AUTO"))
                        i_name = str(row.get(2, ""))
                        try:
                            price = float(row.get(3, 0.0)) if pd.notna(row.get(3)) else 0.0
                        except:
                            price = 0.0
                        unit = str(row.get(4, "Box")) if pd.notna(row.get(4)) else "Box"
                        
                        if pd.notna(i_name) and i_name.strip() != "" and i_name != "nan":
                            new_items_list.append({
                                "Product Code": p_code,
                                "Item Name": i_name,
                                "Category": CATEGORIES_LIST[0],
                                "Unit": unit if unit in UNITS_LIST else "Box",
                                "Stock Balance": 0.0,
                                "Last Price": price,
                                "Supplier": supplier,
                                "Vat Type": "Non Vat"
                            })
                    
                    if len(new_items_list) > 0:
                        df_import = pd.DataFrame(new_items_list)
                        st.session_state['company_inventories'][selected_company] = pd.concat([current_inv, df_import], ignore_index=True).drop_duplicates(subset=["Item Name"], keep="last")
                        st.success(f"นำเข้าสำเร็จ {len(new_items_list)} รายการ!")
                        st.rerun()
                    else:
                        st.error("ไม่พบข้อมูลชื่อสินค้าในไฟล์")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

    with tab_m2:
        st.subheader("เพิ่มข้อมูลวัตถุดิบรายรายการ (Manual Add)")
        existing_suppliers = current_inv['Supplier'].unique().tolist() if len(current_inv) > 0 else ["General", "CP Axtra (Makro)", "CP Axtra (Lotus)"]
        
        with st.form("manual_add_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                m_code = st.text_input("รหัสสินค้า (Product Code / SKU)")
                m_name = st.text_input("ชื่อวัตถุดิบ (Item Name)")
                m_cat = st.selectbox("หมวดหมู่ (Category)", CATEGORIES_LIST)
                m_unit = st.selectbox("หน่วยนับ (Unit)", UNITS_LIST)
            with col_b:
                m_supplier = st.selectbox("ร้านค้าที่ซื้อ (Supplier)", existing_suppliers)
                m_price = st.number_input("ราคาล่าสุดต่อหน่วย (Last Price)", min_value=0.0, value=0.0)
                m_vat = st.selectbox("ประเภทภาษี (Vat Type)", VAT_TYPES_LIST)
                m_qty = st.number_input("จำนวนสต็อกเริ่มต้น (Initial Stock Balance)", min_value=0.0, value=0.0)
            
            submit_manual = st.form_submit_button("💾 บันทึกเพิ่มสินค้า (Save Item)")
            if submit_manual:
                if m_name.strip() != "":
                    new_manual_row = {
                        "Product Code": m_code if m_code else "AUTO",
                        "Item Name": m_name,
                        "Category": m_cat,
                        "Unit": m_unit,
                        "Stock Balance": m_qty,
                        "Last Price": m_price,
                        "Supplier": m_supplier,
                        "Vat Type": m_vat
                    }
                    st.session_state['company_inventories'][selected_company] = pd.concat([current_inv, pd.DataFrame([new_manual_row])], ignore_index=True)
                    st.success(f"เพิ่มสินค้า '{m_name}' สำเร็จเรียบร้อย!")
                    st.rerun()
                else:
                    st.warning("กรุณากรอกชื่อวัตถุดิบ (Item Name)")

# ----------------------------------------------------
# 6. เมนูย่อย 3.3: รับสินค้า (Stock In) ตามข้อ 3
# ----------------------------------------------------
elif selected_menu == t['sub_stock_in']:
    st.title(f"📥 {t['sub_stock_in']} - {selected_company}")
    
    if len(current_inv) > 0:
        st.subheader("🧾 บันทึกรับสินค้าเข้า (Stock In)")
        
        # ฟีเจอร์ AI ถ่ายรูปภาพใบเสร็จแล้วแปลงเป็นข้อๆ
        st.markdown("#### 🤖 ระบบแปลงภาพถ่ายใบเสร็จ / ใบกำกับภาษีอัตโนมัติ (AI Receipt Scanner)")
        receipt_photo = st.file_uploader("ถ่ายรูปหรืออัปโหลดภาพใบเสร็จ (Upload Receipt Image)", type=["jpg", "png", "jpeg"])
        if receipt_photo is not None:
            st.image(receipt_photo, caption="ภาพใบเสร็จที่อัปโหลด", width=300)
            if st.button("🔍 ประมวลผลภาพใบเสร็จด้วย AI"):
                st.success("แปลงข้อมูลสำเร็จ! (ระบบจำลองดึงรายการ: นมจืด 1 ลิตร จำนวน 5 กล่อง ราคา 109 บาท)")
                # บันทึกจำลองลง session สำหรับสินค้าด่วน
                if 'ai_scanned_items' not in st.session_state:
                    st.session_state['ai_scanned_items'] = []
                st.session_state['ai_scanned_items'].append({"Item Name": "นมจืด 1 ลิตร", "Qty": 5.0, "Price": 109.0, "Vat": "Non Vat"})

        st.markdown("---")
        
        # ช่องกรอกหัวเอกสารหลัก
        doc_no = st.text_input("เลขที่เอกสาร (ใบกำกับภาษี / ใบเสร็จรับเงิน / ใบส่งของ)")
        supplier_in = st.text_input("ชื่อร้านค้าที่ซื้อ (Supplier)")
        receipt_image_proof = st.file_uploader("หลักฐานการรับสินค้า (ภาพถ่ายสลิป/ใบเสร็จเพิ่มเติม)", type=["jpg", "png", "jpeg"], key="proof_img")
        
        st.markdown("---")
        st.markdown("#### รายการสินค้าที่รับเข้า")
        
        # ใช้ Session เก็บรายการสินค้าที่จะรับเข้าหลายรายการก่อนกดบันทึกทีเดียว
        if f'temp_stock_in_list_{selected_company}' not in st.session_state:
            st.session_state[f'temp_stock_in_list_{selected_company}'] = []
            
        with st.form("add_item_to_stock_in_form"):
            col_in1, col_in2, col_in3, col_in4 = st.columns(4)
            with col_in1:
                sel_item_in = st.selectbox("เลือกวัตถุดิบ", current_inv['Item Name'].tolist())
            with col_in2:
                q_in = st.number_input("จำนวนรับเข้า", min_value=0.1, value=1.0)
            with col_in3:
                p_in = st.number_input("ราคาต่อหน่วย", min_value=0.0, value=10.0)
            with col_in4:
                v_in = st.selectbox("Vat Type", VAT_TYPES_LIST)
                
            add_to_list_btn = st.form_submit_button("➕ กดเพิ่มรายการสินค้าอื่นเข้าตาราง")
            if add_to_list_btn:
                st.session_state[f'temp_stock_in_list_{selected_company}'].append({
                    "Item Name": sel_item_in,
                    "Quantity": q_in,
                    "Price/Unit": p_in,
                    "Vat Type": v_in
                })
                st.success(f"เพิ่ม {sel_item_in} เข้าในรายการแล้ว")
                
        # แสดงรายการที่เตรียมบันทึก
        temp_list = st.session_state[f'temp_stock_in_list_{selected_company}']
        if len(temp_list) > 0:
            st.write("ตารางรายการสินค้าที่เตรียมรับเข้า:")
            temp_df = pd.DataFrame(temp_list)
            st.dataframe(temp_df, use_container_width=True)
            
            if st.button("💾 กดปุ่มบันทึกทุกรายการที่ล่างสุด (Save All Stock In)"):
                if not doc_no:
                    st.error("กรุณากรอกเลขที่เอกสาร!")
                else:
                    for itm in temp_list:
                        # อัปเดตสต็อกในคลัง
                        item_name = itm["Item Name"]
                        qty = itm["Quantity"]
                        price = itm["Price/Unit"]
                        vat = itm["Vat Type"]
                        
                        idx = current_inv[current_inv['Item Name'] == item_name].index[0]
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] += qty
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Last Price'] = price
                        st.session_state['company_inventories'][selected_company].loc[idx, 'Vat Type'] = vat
                        if supplier_in:
                            st.session_state['company_inventories'][selected_company].loc[idx, 'Supplier'] = supplier_in
                        
                        # บันทึกประวัติ Transaction ทุกอย่าง
                        new_t = {
                            "Company": selected_company,
                            "Date": str(datetime.today().date()),
                            "DocNo": doc_no,
                            "Supplier": supplier_in if supplier_in else "General",
                            "Item Name": item_name,
                            "Quantity": qty,
                            "Price/Unit": price,
                            "Vat Type": vat,
                            "Total Price": qty * price,
                            "Type": "IMPORT",
                            "Receiver": "-",
                            "Department": "-"
                        }
                        st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                    
                    # ล้างค่าชั่วคราว
                    st.session_state[f'temp_stock_in_list_{selected_company}'] = []
                    st.success("บันทึกรับสินค้าทุกรายการเรียบร้อยแล้ว!")
                    st.rerun()
            
            if st.button("🗑️ ล้างรายการที่เลือกทั้งหมด"):
                st.session_state[f'temp_stock_in_list_{selected_company}'] = []
                st.rerun()
        else:
            st.info("ยังไม่มีรายการสินค้า กรุณากดเพิ่มรายการสินค้าเข้ามาก่อน")
    else:
        st.warning("ยังไม่มีรายการสินค้าในสาขานี้ กรุณานำเข้าหรือเพิ่มสินค้าก่อน")

# ----------------------------------------------------
# 7. เมนูย่อย: เบิกสินค้า (Stock Out) ตามข้อ 4
# ----------------------------------------------------
elif selected_menu == t['sub_stock_out']:
    st.title(f"📤 {t['sub_stock_out']} - {selected_company}")
    
    if len(current_inv) > 0:
        with st.form("stock_out_form"):
            selected_item_out = st.selectbox("เลือกวัตถุดิบที่ต้องการเบิก / Select Item", current_inv['Item Name'].tolist())
            item_row = current_inv[current_inv['Item Name'] == selected_item_out].iloc[0]
            
            # เพิ่มหน่วยนับแสดงให้เห็นชัดเจน
            st.info(f"คงเหลือปัจจุบัน: {item_row['Stock Balance']} **{item_row['Unit']}**")
            
            qty_out = st.number_input(f"จำนวนที่ต้องการเบิก (หน่วยนับ: {item_row['Unit']})", min_value=0.1, value=1.0)
            
            # เพิ่มวันที่เบิกสินค้า
            date_out = st.date_input("วันที่เบิกสินค้า", value=datetime.today())
            
            # แยกช่องผู้เบิก กับ แผนกที่นำไปใช้ออกจากกัน
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                requester_out = st.text_input("ชื่อผู้เบิก (Receiver / Requester)")
            with col_o2:
                department_out = st.text_input("แผนกที่นำไปใช้ (Department)")
            
            submit_out = st.form_submit_button("ยืนยันการเบิกสินค้า / Confirm Withdrawal")
            if submit_out:
                if qty_out > item_row['Stock Balance']:
                    st.error("จำนวนคงเหลือไม่พอเบิกออก!")
                elif not requester_out or not department_out:
                    st.error("กรุณากรอกชื่อผู้เบิกและแผนกที่นำไปใช้ให้ครบถ้วน")
                else:
                    idx = current_inv[current_inv['Item Name'] == selected_item_out].index[0]
                    st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] -= qty_out
                    
                    new_t = {
                        "Company": selected_company, 
                        "Date": str(date_out), 
                        "DocNo": f"OUT-{datetime.now().strftime('%m%d%H%M')}",
                        "Supplier": item_row['Supplier'], 
                        "Item Name": selected_item_out,
                        "Quantity": qty_out, 
                        "Price/Unit": item_row['Last Price'], 
                        "Vat Type": item_row.get('Vat Type', 'Non Vat'),
                        "Total Price": qty_out * item_row['Last Price'], 
                        "Type": "EXPORT",
                        "Receiver": requester_out,
                        "Department": department_out
                    }
                    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                    st.success("เบิกสินค้าสำเร็จ!")
                    st.rerun()
    else:
        st.warning("ไม่มีสินค้าในระบบ")

# ----------------------------------------------------
# 8. ประวัติการทำรายการ ตามข้อ 5
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 {t['m_history']} - {selected_company}")
    
    # เพิ่มช่องสำหรับเลือกวันที่ที่ต้องการดูประวัติ
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        history_date = st.date_input("เลือกวันที่ต้องการดูประวัติ", value=datetime.today())
    with col_h2:
        history_type_filter = st.selectbox("ประเภทรายการ", ["ทั้งหมด (All)", "IMPORT (รับเข้า)", "EXPORT (เบิกออก)"])
        
    st.markdown("---")
    
    if len(trans_df) > 0:
        comp_trans = trans_df[trans_df['Company'] == selected_company].copy()
        
        # กรองตามวันที่เลือก
        comp_trans = comp_trans[comp_trans['Date'] == str(history_date)]
        
        if history_type_filter == "IMPORT (รับเข้า)":
            comp_trans = comp_trans[comp_trans['Type'] == 'IMPORT']
        elif history_type_filter == "EXPORT (เบิกออก)":
            comp_trans = comp_trans[comp_trans['Type'] == 'EXPORT']
            
        st.write(f"ประวัติการทำรายการประจำวันที่ {history_date} (แสดงทุกรายการ เช่น การรับของ, เบิกของ)")
        if len(comp_trans) > 0:
            st.dataframe(comp_trans, use_container_width=True)
        else:
            st.info("ไม่พบประวัติการทำรายการในวันที่เลือก")
    else:
        st.info("ยังไม่มีประวัติการทำรายการ")

# ----------------------------------------------------
# 9. ระบบขอซื้อ & ใบสั่งซื้อ (PR & PO) ตามข้อ 6
# ----------------------------------------------------
elif selected_menu == t['m_pr_po']:
    st.title(f"📝 {t['m_pr_po']} - {selected_company}")
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ออกใบสั่งซื้อ (PO) & อนุมัติ"])
    
    with tab1:
        st.subheader("สร้างใบขอซื้อ (Purchase Request - PR)")
        with st.form("pr_form"):
            # 1. เพิ่มวันที่ขอซื้อ
            pr_date = st.date_input("1. วันที่ขอซื้อ", value=datetime.today())
            
            # 2. ซื้อร้านค้าย้ายขึ้นมาเป็นหัวข้อที่ 2 รองจากวันที่
            existing_suppliers = current_inv['Supplier'].unique().tolist() if len(current_inv) > 0 else ["General"]
            pr_sup = st.selectbox("2. เลือกชื่อร้านค้าที่ต้องการซื้อ (Supplier)", existing_suppliers)
            
            # กรองสินค้าเฉพาะร้านค้านั้นๆ
            shop_items = current_inv[current_inv['Supplier'] == pr_sup]['Item Name'].tolist()
            if not shop_items:
                shop_items = current_inv['Item Name'].tolist() if len(current_inv) > 0 else []
                
            # 3. ซื้อวัตถุดิบให้ขึ้นเป็น Dropdown เป็นรายการสินค้าของร้านค้าที่เลือก
            pr_item = st.selectbox("3. เลือกซื้อวัตถุดิบ (Item Name)", shop_items)
            
            # ดึงข้อมูลหน่วยนับและสต็อกคงเหลือมาแสดง
            selected_row_info = current_inv[current_inv['Item Name'] == pr_item].iloc[0] if pr_item and len(current_inv[current_inv['Item Name'] == pr_item]) > 0 else None
            curr_unit_pr = selected_row_info['Unit'] if selected_row_info is not None else "Box"
            curr_stock_pr = selected_row_info['Stock Balance'] if selected_row_info is not None else 0.0
            
            # เพิ่มการแสดงสินค้าคงเหลือของสินค้าแต่ละรายการที่ขอซื้อ
            st.info(f"📦 สินค้าคงเหลือปัจจุบันในคลัง: **{curr_stock_pr} {curr_unit_pr}**")
            
            col_pr1, col_pr2 = st.columns(2)
            with col_pr1:
                pr_qty = st.number_input("จำนวนที่ต้องการขอซื้อ", min_value=0.1, value=1.0)
            with col_pr2:
                # เพิ่มหน่วยนับหลังช่องจำนวน
                st.text_input("หน่วยนับ (Unit)", value=curr_unit_pr, disabled=True)
                
            # เพิ่มช่องผู้ขอซื้อ
            pr_requester = st.text_input("ชื่อผู้ขอซื้อ (Requester Name)", value=user_info['Name'])
            
            sub_pr = st.form_submit_button("ส่งใบขอซื้อ (Submit PR)")
            if sub_pr and pr_item:
                new_pr = {
                    "PR_ID": f"PR-{datetime.now().strftime('%m%d%H%M%S')}",
                    "Date": str(pr_date),
                    "Supplier": pr_sup,
                    "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)",
                    "Requester": pr_requester,
                    "Items": f"{pr_item} จำนวน {pr_qty} {curr_unit_pr}"
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                st.success("สร้างใบขอซื้อ (PR) สำเร็จ! เอกสารถูกส่งไปยังผู้จัดการเพื่ออนุมัติแล้ว")
                st.rerun()
                
        st.markdown("---")
        st.subheader("รายการใบขอซื้อทั้งหมดในระบบ")
        if len(st.session_state['purchase_requests']) > 0:
            st.dataframe(st.session_state['purchase_requests'], use_container_width=True)
        else:
            st.info("ยังไม่มีใบขอซื้อในระบบ")
            
    with tab2:
        st.subheader("📄 ตรวจสอบ อนุมัติ PR และสร้างใบสั่งซื้อ (PO)")
        pr_df = st.session_state['purchase_requests']
        
        if len(pr_df) > 0:
            for idx, row in pr_df.iterrows():
                with st.expander(f"เอกสาร {row['PR_ID']} | ร้าน: {row['Supplier']} | สถานะ: {row['Status']} (วันที่: {row['Date']})"):
                    st.write(f"- **ผู้ขอซื้อ:** {row['Requester']}")
                    st.write(f"- **สาขา:** {row['Branch']}")
                    st.write(f"- **รายการสินค้า:** {row['Items']}")
                    
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("✅ อนุมัติ (Approve)", key=f"app_{idx}"):
                            st.session_state['purchase_requests'].loc[idx, 'Status'] = "Approved (อนุมัติแล้ว)"
                            st.success("อนุมัติเอกสารเรียบร้อยแล้ว!")
                            st.rerun()
                    with col_act2:
                        if st.button("❌ ปฏิเสธ (Reject)", key=f"rej_{idx}"):
                            st.session_state['purchase_requests'].loc[idx, 'Status'] = "Rejected (ไม่อนุมัติ)"
                            st.warning("ปฏิเสธเอกสารแล้ว")
                            st.rerun()
                    with col_act3:
                        if st.button("✏️ แก้ไขรายการ (Edit)", key=f"ed_{idx}"):
                            st.info("สามารถแก้ไขรายละเอียดในระบบหลังบ้านได้")
                            
            st.markdown("---")
            st.subheader("🛒 สร้างใบ PO อัตโนมัติจากใบขอซื้อที่อนุมัติแล้ว")
            approved_prs = pr_df[pr_df['Status'] == "Approved (อนุมัติแล้ว)"]
            if len(approved_prs) > 0:
                approved_ids = approved_prs['PR_ID'].tolist()
                selected_pr_for_po = st.selectbox("เลือกใบ PR ที่อนุมัติแล้วเพื่อออกใบ PO", approved_ids)
                
                if st.button("🖨️ พิมพ์ / สร้างใบสั่งซื้อ (PO) ทางการ"):
                    selected_pr_data = approved_prs[approved_prs['PR_ID'] == selected_pr_for_po].iloc[0]
                    company_addr = st.session_state['company_addresses'].get(selected_company, "ที่อยู่บริษัท...")
                    
                    st.markdown(f"""
                    <div style='border: 2px solid #333; padding: 20px; border-radius: 10px; background-color: white; color: black;'>
                        <h2 style='text-align: center;'>ใบสั่งซื้อ (PURCHASE ORDER - PO)</h2>
                        <hr>
                        <p><b>บริษัท / สาขา:</b> {selected_company}</p>
                        <p><b>ที่อยู่:</b> {company_addr}</p>
                        <p><b>เลขที่ใบ PO / อ้างอิง PR:</b> PO-AUTO-{selected_pr_data['PR_ID']}</p>
                        <p><b>วันที่สั่งซื้อ:</b> {datetime.today().date()}</p>
                        <p><b>ร้านค้า (Supplier):</b> {selected_pr_data['Supplier']}</p>
                        <hr>
                        <h4>รายการสินค้า:</h4>
                        <p>{selected_pr_data['Items']}</p>
                        <hr>
                        <p style='text-align: right;'>ผู้มีอำนาจอนุมัติ: ______________________</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ยังไม่มีใบขอซื้อที่อยู่ในสถานะ 'อนุมัติแล้ว' สำหรับสร้างใบ PO")
        else:
            st.info("ยังไม่มีข้อมูลใบขอซื้อในระบบ")

# ----------------------------------------------------
# 10. รายการสรุปสต็อก & นับสต็อกสิ้นเดือน ตามข้อ 7
# ----------------------------------------------------
elif selected_menu == t['m_eom']:
    st.title(f"📋 {t['m_eom']} - {selected_company}")
    
    st.markdown("#### 🔍 ตัวกรองและช่วงเวลาสินค้า")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        eom_start_date = st.date_input("ตั้งแต่วันที่", value=datetime.today().replace(day=1), key="eom_start")
    with col_e2:
        eom_end_date = st.date_input("ถึงวันที่", value=datetime.today(), key="eom_end")
    with col_e3:
        all_cats_eom = ["ทุกหมวดหมู่"] + CATEGORIES_LIST
        selected_eom_cat = st.selectbox("หมวดหมู่", all_cats_eom, key="eom_cat")
    with col_e4:
        all_sups_eom = ["ทุกร้านค้า"] + (current_inv['Supplier'].unique().tolist() if len(current_inv)>0 else [])
        selected_eom_sup = st.selectbox("ร้านค้า", all_sups_eom, key="eom_sup")
        
    eom_search_kw = st.text_input("🔍 ค้นหาชื่อสินค้า (Search Item Name)", key="eom_kw")
    
    st.markdown("---")
    
    if len(current_inv) > 0:
        filtered_eom = current_inv.copy()
        if selected_eom_cat != "ทุกหมวดหมู่":
            filtered_eom = filtered_eom[filtered_eom['Category'] == selected_eom_cat]
        if selected_eom_sup != "ทุกร้านค้า":
            filtered_eom = filtered_eom[filtered_eom['Supplier'] == selected_eom_sup]
        if eom_search_kw.strip() != "":
            kw = eom_search_kw.strip().lower()
            filtered_eom = filtered_eom[filtered_eom['Item Name'].str.lower().str.contains(kw, na=False)]
            
        st.write(f"แสดงรายการสินค้าสำหรับนับสต็อก (ช่วงวันที่ {eom_start_date} ถึง {eom_end_date})")
        
        count_df = filtered_eom[['Item Name', 'Category', 'Unit', 'Stock Balance', 'Supplier']].copy()
        count_df.rename(columns={'Stock Balance': 'System Balance (ยอดในระบบ)'}, inplace=True)
        count_df['Actual Count (ยอดนับจริง)'] = count_df['System Balance (ยอดในระบบ)']
        
        edited_df = st.data_editor(
            count_df,
            column_config={"Actual Count (ยอดนับจริง)": st.column_config.NumberColumn(min_value=0.0, step=0.1)},
            disabled=["Item Name", "Category", "Unit", "System Balance (ยอดในระบบ)", "Supplier"],
            use_container_width=True
        )
        
        if st.button("💾 บันทึกและปรับปรุงยอดสต็อกสิ้นเดือน"):
            for idx, row in edited_df.iterrows():
                item_name = row['Item Name']
                actual_val = row['Actual Count (ยอดนับจริง)']
                orig_idx = current_inv[current_inv['Item Name'] == item_name].index[0]
                st.session_state['company_inventories'][selected_company].loc[orig_idx, 'Stock Balance'] = actual_val
            st.success("บันทึกยอดนับสต็อกสิ้นเดือนเรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลสินค้าในสาขานี้")

# ----------------------------------------------------
# 11. แถบเมนูหลัก: ตั้งค่าข้อมูลบริษัท (ตามข้อ 8)
# ----------------------------------------------------
elif selected_menu == t['m_company_settings']:
    st.title(f"🏢 ตั้งค่าข้อมูลบริษัทและแอดมิน - {selected_company}")
    
    set_tab1, set_tab2 = st.tabs(["📄 1. แก้ไข/เพิ่มชื่อ ที่อยู่ หรือข้อมูลบริษัทอื่นๆ", "⚙️ 2. การจัดการการจัดการแอดมินและสิทธิ์"])
    
    with set_tab1:
        st.subheader("แก้ไขชื่อ ที่อยู่ และข้อมูลบริษัท")
        current_addr = st.session_state['company_addresses'].get(selected_company, "")
        
        with st.form("company_info_form"):
            new_comp_name = st.text_input("ชื่อบริษัท / สาขา", value=selected_company)
            new_comp_address = st.text_area("ที่อยู่ของร้านค้า / สาขา", value=current_addr)
            new_tax_id = st.text_input("เลขประจำตัวผู้เสียภาษี (Tax ID)", value="01055xxxxxxxx")
            new_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ", value="02-xxx-xxxx")
            
            save_comp_info = st.form_submit_button("💾 บันทึกข้อมูลบริษัท")
            if save_comp_info:
                st.session_state['company_addresses'][selected_company] = new_comp_address
                st.success("บันทึกข้อมูลที่อยู่และรายละเอียดบริษัทเรียบร้อยแล้ว!")
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

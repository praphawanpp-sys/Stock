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
        "sub_import_excel": "📥 3.1 นำเข้าสินค้า (Excel & Manual)",
        "sub_stock_in": "📥 3.2 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 3.3 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อกสิ้นเดือน",
        "m_admin": "⚙️ จัดการแอดมินและสิทธิ์",
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
        "sub_import_excel": "📥 3.1 Import Items (Excel & Manual)",
        "sub_stock_in": "📥 3.2 Stock In",
        "sub_stock_out": "📤 3.3 Stock Out / Requisition",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_eom": "📋 Stock Summary & End of Month Count",
        "m_admin": "⚙️ Admin & Permissions",
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
        {"Company": COMPANIES[0], "Date": str(datetime.today().date()), "Supplier": "CP Axtra (Makro)", "Item Name": "นมจืด 1 ลิตร", "Quantity": 25.0, "Price/Unit": 109.0, "Vat Type": "Non Vat", "Total Price": 2725.0, "Type": "IMPORT"}
    ])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": COMPANIES[0], "Role": "Manager"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "SKU", "Name", "Qty", "Supplier", "Branch", "Status", "Requester"])

# ----------------------------------------------------
# 2. Sidebar: เลือกภาษา บริษัท และผู้ใช้งาน
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
    
    selected_menu = st.radio("Navigation", [
        t['m_dashboard'],
        t['m_inventory_mgmt'],
        t['sub_import_excel'],
        t['sub_stock_in'],
        t['sub_stock_out'],
        t['m_history'],
        t['m_pr_po'],
        t['m_eom'],
        t['m_admin']
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
# 4. เมนูที่ 2: การจัดการรายการสินค้า (Inventory Management) + ปุ่มแก้ไข/ลบ ทุกบรรทัด
# ----------------------------------------------------
elif selected_menu == t['m_inventory_mgmt']:
    st.title(f"📦 {t['m_inventory_mgmt']} - {selected_company}")
    
    st.markdown("#### 🔍 ค้นหาและกรองข้อมูลสินค้าตามร้านค้า (Filter by Supplier)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        all_suppliers_mgmt = ["ทั้งหมดทุกร้านค้า (All Suppliers)"] + (current_inv['Supplier'].unique().tolist() if len(current_inv)>0 else [])
        selected_mgmt_supplier = st.selectbox("เลือกตามร้านค้าที่ซื้อ (Select Supplier)", all_suppliers_mgmt)
    with col_m2:
        search_mgmt_keyword = st.text_input("🔍 ค้นหาด้วยชื่อสินค้า หรือ รหัสสินค้า (Search Name / Code)")
        
    st.markdown("---")
    
    mgmt_filtered = current_inv.copy()
    if selected_mgmt_supplier != "ทั้งหมดทุกร้านค้า (All Suppliers)":
        mgmt_filtered = mgmt_filtered[mgmt_filtered['Supplier'] == selected_mgmt_supplier]
    if search_mgmt_keyword.strip() != "":
        kw = search_mgmt_keyword.strip().lower()
        mgmt_filtered = mgmt_filtered[
            mgmt_filtered['Item Name'].str.lower().str.contains(kw, na=False) |
            mgmt_filtered['Product Code'].str.lower().str.contains(kw, na=False)
        ]
        
    st.subheader(f"📋 รายการสินค้าทั้งหมด ({len(mgmt_filtered)} รายการ)")
    
    if len(mgmt_filtered) > 0:
        # หัวตารางจำลอง
        h_col = st.columns([1.2, 2.2, 2.2, 1, 0.8, 0.8, 1.5, 1, 1.2])
        headers = ["Product Code", "Item Name", "Category", "Unit", "Stock", "Price", "Supplier", "Vat Type", "จัดการ"]
        for hc, h_text in zip(h_col, headers):
            hc.markdown(f"**{h_text}**")
        st.markdown("---")
        
        # วนลูปแสดงข้อมูลทีละบรรทัด พร้อมปุ่มแก้ไข/ลบที่ท้ายแถว
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
                    st.session_state[f'edit_target_{selected_company}'] = idx
            with r_col[9]:
                if st.button("🗑️", key=f"del_btn_{idx}", help="ลบรายการนี้"):
                    st.session_state['company_inventories'][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                    st.success(f"ลบรายการ {row['Item Name']} สำเร็จ!")
                    st.rerun()
                    
        # หากมีการกดปุ่มแก้ไข ให้แสดงฟอร์มแบบ Dropdown
        active_edit_idx = st.session_state.get(f'edit_target_{selected_company}', None)
        if active_edit_idx is not None and active_edit_idx in current_inv.index:
            st.markdown("---")
            st.subheader(f"🛠️ แก้ไขข้อมูลสินค้า: {current_inv.loc[active_edit_idx, 'Item Name']}")
            item_data = current_inv.loc[active_edit_idx]
            
            existing_suppliers = current_inv['Supplier'].unique().tolist()
            if not existing_suppliers:
                existing_suppliers = ["General", "CP Axtra (Makro)", "CP Axtra (Lotus)", "กส-สรา ค้าส่ง"]

            with st.form(f"inline_edit_form_{active_edit_idx}"):
                e_code = st.text_input("รหัสสินค้า (Product Code)", value=str(item_data['Product Code']))
                e_name = st.text_input("ชื่อวัตถุดิบ (Item Name)", value=str(item_data['Item Name']))
                
                # Dropdown: Category
                curr_cat = str(item_data['Category'])
                cat_idx = CATEGORIES_LIST.index(curr_cat) if curr_cat in CATEGORIES_LIST else 0
                e_cat = st.selectbox("หมวดหมู่ (Category)", CATEGORIES_LIST, index=cat_idx)
                
                # Dropdown: Unit
                curr_unit = str(item_data['Unit'])
                unit_idx = UNITS_LIST.index(curr_unit) if curr_unit in UNITS_LIST else 0
                e_unit = st.selectbox("หน่วยนับ (Unit)", UNITS_LIST, index=unit_idx)
                
                e_bal = st.number_input("จำนวนสต็อก (Stock Balance)", value=float(item_data['Stock Balance']))
                e_price = st.number_input("ราคาล่าสุด (Last Price)", value=float(item_data['Last Price']))
                
                # Dropdown: Supplier
                curr_sup = str(item_data['Supplier'])
                sup_idx = existing_suppliers.index(curr_sup) if curr_sup in existing_suppliers else 0
                e_sup = st.selectbox("ร้านค้าที่ซื้อ (Supplier)", existing_suppliers, index=sup_idx)
                
                # Dropdown: Vat Type
                curr_vat = str(item_data.get('Vat Type', 'Non Vat'))
                vat_idx = VAT_TYPES_LIST.index(curr_vat) if curr_vat in VAT_TYPES_LIST else 0
                e_vat = st.selectbox("ประเภทภาษี (Vat Type)", VAT_TYPES_LIST, index=vat_idx)
                
                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    save_edit = st.form_submit_button("💾 บันทึกการแก้ไข")
                with col_sub2:
                    cancel_edit = st.form_submit_button("❌ ยกเลิก")
                    
                if save_edit:
                    st.session_state['company_inventories'][selected_company].loc[active_edit_idx] = [e_code, e_name, e_cat, e_unit, e_bal, e_price, e_sup, e_vat]
                    del st.session_state[f'edit_target_{selected_company}']
                    st.success("บันทึกการแก้ไขสำเร็จ!")
                    st.rerun()
                elif cancel_edit:
                    del st.session_state[f'edit_target_{selected_company}']
                    st.rerun()
    else:
        st.info("ไม่พบรายการสินค้าตามเงื่อนไขที่เลือก")

# ----------------------------------------------------
# 5. เมนูย่อย 3.1: นำเข้าสินค้า (Excel Import & Manual Add)
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
# 6. เมนูย่อย 3.2: รับสินค้า (Stock In)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_in']:
    st.title(f"📥 {t['sub_stock_in']} - {selected_company}")
    
    if len(current_inv) > 0:
        with st.form("stock_in_form"):
            selected_item = st.selectbox("เลือกวัตถุดิบ / Select Item", current_inv['Item Name'].tolist())
            supplier_in = st.text_input("Supplier Name / ชื่อร้านค้าที่ซื้อ")
            qty_in = st.number_input("Quantity / จำนวนรับเข้า", min_value=0.1, value=1.0)
            price_in = st.number_input("Price per Unit / ราคาต่อหน่วย", min_value=0.0, value=10.0)
            vat_in = st.selectbox("ประเภทภาษี (Vat Type)", VAT_TYPES_LIST)
            
            submit_in = st.form_submit_button("บันทึกรับเข้าสินค้า / Confirm Stock In")
            if submit_in:
                idx = current_inv[current_inv['Item Name'] == selected_item].index[0]
                st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] += qty_in
                st.session_state['company_inventories'][selected_company].loc[idx, 'Last Price'] = price_in
                st.session_state['company_inventories'][selected_company].loc[idx, 'Vat Type'] = vat_in
                if supplier_in:
                    st.session_state['company_inventories'][selected_company].loc[idx, 'Supplier'] = supplier_in
                
                new_t = {
                    "Company": selected_company, "Date": str(datetime.today().date()),
                    "Supplier": supplier_in if supplier_in else "General", "Item Name": selected_item,
                    "Quantity": qty_in, "Price/Unit": price_in, "Vat Type": vat_in,
                    "Total Price": qty_in * price_in, "Type": "IMPORT"
                }
                st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                st.success("บันทึกรับเข้าสินค้าเรียบร้อย!")
                st.rerun()
    else:
        st.warning("ยังไม่มีรายการสินค้าในสาขานี้ กรุณานำเข้าหรือเพิ่มสินค้าก่อน")

# ----------------------------------------------------
# 7. เมนูย่อย 3.3: เบิกสินค้า (Stock Out)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_out']:
    st.title(f"📤 {t['sub_stock_out']} - {selected_company}")
    
    if len(current_inv) > 0:
        with st.form("stock_out_form"):
            selected_item_out = st.selectbox("เลือกวัตถุดิบที่ต้องการเบิก / Select Item", current_inv['Item Name'].tolist())
            item_row = current_inv[current_inv['Item Name'] == selected_item_out].iloc[0]
            st.info(f"คงเหลือปัจจุบัน: {item_row['Stock Balance']} {item_row['Unit']}")
            
            qty_out = st.number_input("จำนวนที่ต้องการเบิก / Withdrawal Qty", min_value=0.1, value=1.0)
            receiver = st.text_input("ชื่อผู้เบิก / แผนกที่นำไปใช้")
            
            submit_out = st.form_submit_button("ยืนยันการเบิกสินค้า / Confirm Withdrawal")
            if submit_out:
                if qty_out > item_row['Stock Balance']:
                    st.error("จำนวนคงเหลือไม่พอเบิกออก!")
                else:
                    idx = current_inv[current_inv['Item Name'] == selected_item_out].index[0]
                    st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] -= qty_out
                    
                    new_t = {
                        "Company": selected_company, "Date": str(datetime.today().date()),
                        "Supplier": item_row['Supplier'], "Item Name": selected_item_out,
                        "Quantity": qty_out, "Price/Unit": item_row['Last Price'], "Vat Type": item_row.get('Vat Type', 'Non Vat'),
                        "Total Price": qty_out * item_row['Last Price'], "Type": "EXPORT"
                    }
                    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                    st.success("เบิกสินค้าสำเร็จ!")
                    st.rerun()
    else:
        st.warning("ไม่มีสินค้าในระบบ")

# ----------------------------------------------------
# 8. ประวัติการทำรายการ (History)
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 {t['m_history']} - {selected_company}")
    if len(trans_df) > 0:
        comp_trans = trans_df[trans_df['Company'] == selected_company]
        st.dataframe(comp_trans, use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการทำรายการ")

# ----------------------------------------------------
# 9. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)
# ----------------------------------------------------
elif selected_menu == t['m_pr_po']:
    st.title(f"📝 {t['m_pr_po']} - {selected_company}")
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ออกใบสั่งซื้อ (PO)"])
    with tab1:
        with st.form("pr_form"):
            pr_item = st.text_input("ชื่อวัตถุดิบที่ต้องการสั่งซื้อ")
            pr_qty = st.number_input("จำนวน", min_value=1.0, value=10.0)
            pr_sup = st.text_input("ชื่อ Supplier / ร้านค้า")
            sub_pr = st.form_submit_button("ส่งคำขอซื้อ (Submit PR)")
            if sub_pr and pr_item and pr_sup:
                new_pr = {
                    "PR_ID": f"PR-{datetime.now().strftime('%m%d%H%M')}",
                    "Date": str(datetime.today()), "SKU": "AUTO", "Name": pr_item,
                    "Qty": pr_qty, "Supplier": pr_sup, "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)", "Requester": user_info['Name']
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                st.success("สร้าง PR สำเร็จ!")
                st.rerun()
        st.dataframe(st.session_state['purchase_requests'], use_container_width=True)
    with tab2:
        st.write("เลือก PR ที่ได้รับการอนุมัติเพื่อพิมพ์ใบ PO ทางการ")

# ----------------------------------------------------
# 10. รายการสรุปสต็อกและนับสต็อกสิ้นเดือน (End of Month Count)
# ----------------------------------------------------
elif selected_menu == t['m_eom']:
    st.title(f"📋 {t['m_eom']} - {selected_company}")
    if len(current_inv) > 0:
        st.write("กรุณากรอกยอดนับจริง (Actual Count) ประจำสิ้นเดือน เพื่อปรับปรุงยอดสต็อกให้ตรงกับหน้างานจริง")
        
        count_df = current_inv[['Item Name', 'Category', 'Unit', 'Stock Balance']].copy()
        count_df.rename(columns={'Stock Balance': 'System Balance (ยอดในระบบ)'}, inplace=True)
        count_df['Actual Count (ยอดนับจริง)'] = count_df['System Balance (ยอดในระบบ)']
        
        edited_df = st.data_editor(
            count_df,
            column_config={"Actual Count (ยอดนับจริง)": st.column_config.NumberColumn(min_value=0.0, step=0.1)},
            disabled=["Item Name", "Category", "Unit", "System Balance (ยอดในระบบ)"],
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
# 11. จัดการแอดมินและสิทธิ์
# ----------------------------------------------------
elif selected_menu == t['m_admin']:
    st.title(f"⚙️ {t['m_admin']}")
    if user_info['Role'] != "Super Admin":
        st.error("เฉพาะ Super Admin เท่านั้นที่เข้าถึงหน้านี้ได้")
    else:
        st.dataframe(st.session_state['admins'], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🛠️ จัดการผู้ดูแลระบบ (Edit / Delete Admin)")
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
